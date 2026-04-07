"""
Celery tasks для асинхронной обработки запросов к LLM.

Функционал:
- Отправка запросов к OpenRouter API
- Обновление статусов сообщений в БД
- Идемпотентность по task_id / idempotency_key
- Rate limiting через Redis
- Обработка ошибок и повторные попытки
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import UUID

from celery import Task
from celery.utils.log import get_task_logger
from sqlalchemy.ext.asyncio import async_sessionmaker

from chat_api_service.app.consts.message import MessageStatus
from chat_api_service.app.core.config import settings
from chat_api_service.app.db.models import Message
from chat_api_service.app.db.session import DBSession
from chat_api_service.app.infra.redis import RedisClient
from chat_api_service.app.repositories.message import MessageRepository
from chat_api_service.app.services.openrouter_client import OpenRouterClient
from chat_api_service.app.schemas.config import OpenRouterConfig
from chat_api_service.app.infra.celery_app import celery_app
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from chat_api_service.app.consts.llm_tasks import LLMTasksStatus
from chat_api_service.app.schemas.llm_tasks import LLMTaskStatusSchema
from chat_api_service.app.usecases.chat_new_message import ChatNewMessageUsecase
from chat_api_service.app.core.exceptions.value import UUIDValueError


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
            result: LLMTaskStatusSchema = await usecase.new_message()
            return result.to_dict()
    except UUIDValueError as err:
        return {
            "error": f"invalid_uuid: {err.message}",
            "message_id": message_id
        }


@celery_app.task(
    name="chat_api_service.mark_message_read",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2},
)
async def mark_message_read(
        self: Task,
        message_id: str,
        user_id: str,
) -> dict:
    """
    Фоновая задача: обновление статуса сообщения на "прочитано".

    Может вызываться при открытии диалога пользователем или по таймеру.

    :param message_id: UUID сообщения.
    :param user_id: ID пользователя (для проверки прав).
    :return: Результат операции.
    """
    from uuid import UUID

    try:
        msg_uuid = UUID(message_id)
    except (ValueError, AttributeError):
        return {"error": "invalid_message_id"}

    async with DBSession.get_async_session() as session:
        repo = MessageRepository(session)

        message = await repo.get_by_id(msg_uuid)
        if not message:
            return {"error": "message_not_found", "message_id": message_id}

        # Опционально: проверка принадлежности диалога пользователю
        # (можно добавить в репозиторий метод get_conversation_user_id)

        try:
            await repo.update_status(msg_uuid, MessageStatus.READ)
            logger.info(
                f"Message {message_id} marked as read by user {user_id}")

            return {
                "status": "success",
                "message_id": message_id,
                "read_at": message.read_at.isoformat() if message.read_at else None,
            }
        except ValueError as e:
            # Недопустимый переход статуса
            logger.warning(f"Cannot mark message {message_id} as read: {e}")
            return {
                "status": "invalid_transition",
                "message_id": message_id,
                "current_status": message.status.value,
                "error": str(e),
            }


# =============================================================================
# Celery Task: периодическая очистка устаревших блокировок (опционально)
# =============================================================================

@celery_app.task(
    name="chat_api_service.cleanup_stale_locks",
    ignore_result=True,
)
async def cleanup_stale_locks() -> dict:
    """
    Периодическая задача: очистка "зависших" блокировок в Redis.

    Запускается по расписанию (например, раз в 5 минут через Celery Beat).
    """
    redis = RedisClient.client()
    pattern = "llm:lock:*"
    deleted_count = 0

    # Итерируем по ключам с паттерном (в продакшене лучше использовать
    # отдельный set с таймстемпами для более эффективной очистки)
    async for key in redis.scan_iter(match=pattern, count=100):
        ttl = await redis.ttl(key)
        if ttl == -2:  # ключ не существует
            continue
        if ttl > settings.redis.lock_ttl:
            # Блокировка живёт дольше положенного — удаляем
            await redis.delete(key)
            deleted_count += 1
            logger.debug(f"Deleted stale lock: {key.decode()}")

    logger.info(f"Cleanup completed: removed {deleted_count} stale locks")
    return {"deleted_locks": deleted_count}