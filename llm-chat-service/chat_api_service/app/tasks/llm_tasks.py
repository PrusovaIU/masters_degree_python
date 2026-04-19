from datetime import datetime
from functools import wraps
from typing import Callable
from uuid import UUID

from celery import Task
from celery.utils.log import get_task_logger

from chat_api_service.app.core.config import settings
from chat_api_service.app.db.session import DBSession
from chat_api_service.app.infra.redis import RedisClient
from chat_api_service.app.repositories.message import MessageRepository
from chat_api_service.app.services.openrouter_client import OpenRouterClient
from chat_api_service.app.infra.celery_app import celery_app
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from chat_api_service.app.schemas.llm_tasks import LLMTaskStatusSchema
from chat_api_service.app.usecases.chat.handle_message import ChatNewMessageUsecase
from chat_api_service.app.core.exceptions.value import UUIDValueError
from chat_api_service.app.core.exceptions import chat_new_message as chat_nm_exc
from chat_api_service.app.consts.llm_tasks import LLMTasksStatus
from chat_api_service.app.core.exceptions.message import InvalidMessageStatus, MessageNotFound
from chat_api_service.app.usecases.chat.mark_message import MarkMessageUsecase


logger = get_task_logger(__name__)
or_client = OpenRouterClient(settings.openrouter)


@asynccontextmanager
async def _get_message_repo() -> AsyncGenerator[MessageRepository]:
    """
    Создание репозитория для работы с сообщениями.

    :return: Репозиторий MessageRepository.
    """
    async with DBSession.get_async_session() as session:
        repo = MessageRepository(session)
        yield repo


def _uuid_from_str(s: str) -> UUID:
    """
    Конвертация строки в UUID.

    :param s: Строка с UUID.
    :return: UUID.

    :raise UUIDValueError: при невалидном UUID.
    """
    try:
        return UUID(s)
    except Exception as err:
        logger.error(
            f"Невалидное значение UUID: {s} - "
            f"{err} ({err.__class__.__name__})"
        )
        raise UUIDValueError(s)


def uuid_error_decorator(func: Callable):
    """Декоратор для обработки ошибок UUID."""
    @wraps(func)
    async def wrapper(self, message_id, *args, **kwargs) -> dict:
        try:
            return await func(self, message_id, *args, **kwargs)
        except UUIDValueError as err:
            return LLMTaskStatusSchema(
                status=LLMTasksStatus.ERROR,
                message_id=message_id,
                error=f"invalid_uuid: {err.message}",
                error_type=err.__class__.__name__
            ).to_dict()
    return wrapper


@celery_app.task(
    name="chat_api_service.llm_request",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    soft_time_limit=settings.redis.rate_limit.llm_window,
    time_limit=settings.redis.rate_limit.llm_window + 30
)
@uuid_error_decorator
async def llm_request(
        self: Task,
        message_id: str,
        conversation_id: str,
        user_id: str,
        content: str,
        idempotency_key: str,
        temperature: float = 0.7,
) -> dict:
    """
    Асинхронная задача: отправка запроса к LLM и обработка ответа.

    :param message_id: ID сообщения-запроса.
    :param conversation_id: ID диалога.
    :param user_id: Идентификатор пользователя из Auth Service.
    :param content: Текст сообщения пользователя.
    :param idempotency_key: Уникальный ключ для предотвращения дубликатов.
    :param temperature: Параметр креативности модели.

    :return: dict с результатом обработки.

    :raises: Celery Retry при временных ошибках,
             или возврат dict с error при критических сбоях.
    """
    await RedisClient.setup(settings.redis, True)
    status: LLMTaskStatusSchema | None = None
    try:
        message_uuid = _uuid_from_str(message_id)
        conversation_uuid = _uuid_from_str(conversation_id)
        async with _get_message_repo() as repo:
            usecase = ChatNewMessageUsecase(
                repo,
                or_client,
                self,
                message_uuid,
                conversation_uuid,
                user_id,
                content,
                idempotency_key,
                temperature,
                logger
            )
            answer_id, answer_content = await usecase.new_message()
            status = LLMTaskStatusSchema(
                status=LLMTasksStatus.SUCCESS,
                message_id=message_id,
                response_id=str(answer_id),
                content=answer_content,
                task_id=self.request.id
            )
    except chat_nm_exc.RateLimitExceededError:
        status = LLMTaskStatusSchema(
            status=LLMTasksStatus.RATE_LIMITED,
            message_id=message_id,
            retry_after=settings.redis.rate_limit.llm_window
        )
    except chat_nm_exc.CachedError as err:
        status = LLMTaskStatusSchema(
            status=LLMTasksStatus.CACHED,
            message_id=message_id,
            content=err.content
        )
    except chat_nm_exc.AlreadyProcessedError as err:
        status = LLMTaskStatusSchema(
            status=LLMTasksStatus.ALREADY_PROCESSED,
            message_id=message_id,
            content=err.content
        )
    except chat_nm_exc.IsProcessingError:
        status = LLMTaskStatusSchema(
            status=LLMTasksStatus.PROCESSING,
            message_id=message_id,
            note="Request is being processed by another worker"
        )
    except Exception as err:
        if isinstance(err, (ConnectionError, TimeoutError)):
            # Временные ошибки сети — можно повторить
            raise self.retry(
                exc=err,
                countdown=5 * (self.request.retries + 1)
            )
        elif "rate_limit" in str(err).lower():
            # Rate limit от OpenRouter — ждём дольше
            raise self.retry(exc=err, countdown=30)
        else:
            # Критическая ошибка
            status = LLMTaskStatusSchema(
                status=LLMTasksStatus.ERROR,
                message_id=message_id,
                error_type=err.__class__.__name__,
                error=str(err),
                task_id=self.request.id
            )
    return status.model_dump()


@celery_app.task(
    name="chat_api_service.mark_message_read",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2},
)
@uuid_error_decorator
async def mark_message_read(
        self: Task,
        message_id: str,
        user_id: str
) -> dict:
    """
    Фоновая задача: обновление статуса сообщения на "прочитано".

    Может вызываться при открытии диалога пользователем или по таймеру.

    :param message_id: UUID сообщения.
    :param user_id: ID пользователя.
    :return: Результат операции.
    """
    status: LLMTaskStatusSchema | None = None
    try:
        message_uuid = _uuid_from_str(message_id)
        async with _get_message_repo() as repo:
            usecase = MarkMessageUsecase(repo, logger)
            read_at: datetime | None = await usecase.as_read(
                message_uuid, user_id
            )
            read_at_note = read_at.isoformat() if read_at else ""
            status = LLMTaskStatusSchema(
                status=LLMTasksStatus.SUCCESS,
                message_id=message_id,
                note=f"read_at: {read_at_note}"
            )
    except InvalidMessageStatus as err:
        logger.error(
            f"Не удалось пометить сообщение {message_id} как прочитанное: "
            f"{err} ({err.__class__.__name__})"
        )
        status = LLMTaskStatusSchema(
            status=LLMTasksStatus.ERROR,
            message_id=message_id,
            error=str(err),
            error_type=err.__class__.__name__,
            note=f"current_status: {err.old_status}"
        )
    except MessageNotFound as err:
        logger.error(
            f"{err}: message_id={message_id} - {err.__class__.__name__}"
        )
        status = LLMTaskStatusSchema(
            status=LLMTasksStatus.ERROR,
            message_id=message_id,
            error="message_not_found"
        )
    return status.to_dict()


@celery_app.task(
    name="chat_api_service.cleanup_stale_locks",
    ignore_result=True,
)
async def cleanup_stale_locks() -> dict:
    """
    Периодическая задача: очистка "зависших" блокировок в Redis.

    Запускается по расписанию (например, раз в 5 минут через Celery Beat).
    """
    try:
        deleted_count: int = await RedisClient.clean_up()
        logger.info(
            f"Очистка блоков : удалено {deleted_count} зависших блоков"
        )
        return {"deleted_locks": deleted_count}
    except Exception as err:
        logger.error(
            f"Ошибка при очистке блоков: {err} ({err.__class__.__name__})"
        )
        return {"error": str(err)}