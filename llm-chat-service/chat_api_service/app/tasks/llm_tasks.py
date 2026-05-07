from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import wraps
from typing import Callable
from uuid import UUID

from celery import Task
from celery.utils.log import get_task_logger

from chat_api_service.app.core.config import settings
from chat_api_service.app.core.exceptions import \
    chat_new_message as chat_nm_exc
from chat_api_service.app.core.exceptions.value import UUIDValueError
from chat_api_service.app.db.session import DBSession
from chat_api_service.app.infra.celery_app import celery_app
from chat_api_service.app.infra.rabbitmq import RabbitMQClient
from chat_api_service.app.infra.redis import RedisClient
from chat_api_service.app.repositories.message import MessageRepository
from chat_api_service.app.services.openrouter_client import OpenRouterClient
from chat_api_service.app.usecases.chat.handle_message import \
    ChatNewMessageUsecase
from libs.consts.llm_tasks import LLMTasksStatus
from libs.schemas.llm import LLMTaskStatusSchema

logger = get_task_logger(__name__)
or_client = OpenRouterClient(settings.openrouter)
DBSession.setup(settings.db.database_url, settings.db.db_schema, True)


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
    await RabbitMQClient.setup(
        settings.rabbitmq.url,
        settings.rabbitmq.message_queue,
        has_set=True
    )
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
                settings.rabbitmq.message_queue,
                temperature
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
