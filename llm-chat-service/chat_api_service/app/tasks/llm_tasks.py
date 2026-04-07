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
from chat_api_service.app.usecases.chat import ChatNewMessageUsecase

logger = get_task_logger(__name__)

# @asynccontextmanager
# async def _get_message_repo() -> AsyncGenerator[MessageRepository]:
#     """
#     Создание репозитория для работы с сообщениями.
#
#     :return: репозиторий MessageRepository.
#     """
#     async with DBSession.get_async_session() as session:
#         repo = MessageRepository(session)
#         yield repo


# async def _update_message_status(
#         message_id: UUID,
#         new_status: MessageStatus,
#         content: str | None = None,
#         metadata: dict | None = None,
# ) -> None:
#     """
#     Обновление статуса и данных сообщения в БД.
#
#     :param message_id: UUID сообщения.
#     :param new_status: Новый статус.
#     :param content: Опционально новый контент (ответ LLM).
#     :param metadata: Опционально метаданные (токены, модель, и т.д.).
#     """
#     async with _get_message_repo() as repo:
#         if content is not None or metadata is not None:
#             await repo.update_content_and_metadata(
#                 message_id=message_id,
#                 content=content,
#                 metadata=metadata,
#             )
#         await repo.update_status(
#             message_id=message_id,
#             new_status=new_status,
#         )

# async def _check_rate_limit(
#         user_id: str,
#         message_id: UUID
# ) -> LLMTaskStatusSchema | None:
#     """
#     Проверка на превышение лимита запросов.
#
#     :param user_id: Идентификатор пользователя из Auth Service.
#     :param message_id: UUID сообщения-запроса.
#     :return: Статус ошибки, если превышен лимит, иначе None.
#     """
#     if not await RedisClient.check_rate_limit(user_id):
#         logger.warning(
#             f"Rate limit было превышено для пользователя {user_id}. "
#             f"Ключ: {RedisClient.get_rate_limit_key(user_id)}"
#         )
#         await _update_message_status(
#             message_id=message_id,
#             new_status=MessageStatus.FAILED,
#             metadata={"error": "rate_limit_exceeded"}
#         )
#         return LLMTaskStatusSchema(
#             status=LLMTasksStatus.RATE_LIMITED,
#             message_id=message_id,
#             retry_after=settings.redis.rate_limit.llm_window
#         )
#     return None


# async def _acquire_lock(
#         idempotency_key: str,
#         message_id: UUID
# ) -> LLMTaskStatusSchema | None:
#     """
#     Захват блокировки для предотвращения дубликатов.
#
#     :param idempotency_key: Ключ для идентификации запроса.
#     :param message_id: ID сообщения.
#     :return: Статус ошибки, если блокировка уже занята, иначе None.
#     """
#     lock_acquired = await RedisClient.acquire_lock(idempotency_key)
#     if not lock_acquired:
#         # Блокировка уже занята. Возможно, запрос уже обрабатывается.
#         # Проверка на уже обработанный запрос:
#         async with _get_message_repo() as repo:
#             existing: Message | None = \
#                 await repo.get_by_idempotency_key(idempotency_key)
#
#             if existing and existing.status in (
#                     MessageStatus.DELIVERED, MessageStatus.READ
#             ):
#                 logger.info(
#                     f"Идемпотентный запрос уже обработан: {idempotency_key}"
#                 )
#                 return LLMTaskStatusSchema(
#                     status=LLMTasksStatus.ALREADY_PROCESSED,
#                     message_id=message_id,
#                     content=existing.content
#                 )
#             else:
#                 return LLMTaskStatusSchema(
#                     status=LLMTasksStatus.PROCESSING,
#                     message_id=message_id,
#                     note="Request is being processed by another worker"
#                 )
#     return None


# async def _check_race_condition(
#         self: Task,
#         message_id: UUID,
#         idempotency_key: str
# ) -> LLMTaskStatusSchema | None:
#     """
#     Проверка на race condition при обработке запроса.
#
#     :param self: Задача Celery.
#     :param message_id: ID сообщения.
#     :param idempotency_key: Ключ для идентификации запроса.
#     :return: Статус ошибки, если запрос уже обрабатывается, иначе None.
#     """
#     async with _get_message_repo() as repo:
#         existing_msg = await repo.get_by_idempotency_key(idempotency_key)
#         if existing_msg:
#             if existing_msg.status in (
#                     MessageStatus.DELIVERED, MessageStatus.READ
#             ):
#                 logger.info(
#                     f"Обнаружено дублирование запроса: {idempotency_key}"
#                 )
#                 return LLMTaskStatusSchema(
#                     status=LLMTasksStatus.CACHED,
#                     message_id=str(existing_msg.id),
#                     content=existing_msg.content
#                 )
#             elif existing_msg.status == MessageStatus.PROCESSING:
#                 return LLMTaskStatusSchema(
#                     status=LLMTasksStatus.PROCESSING,
#                     message_id=message_id
#                 )
#         await repo.update_status(message_id, MessageStatus.PROCESSING)
#         await repo.update_llm_task_id(message_id, self.request.id)
#     return None


# async def _prepare_context(
#         conversation_id: UUID
# ):
#     async with _get_message_repo() as repo:
#         # Получение последних сообщений для контекста
#         history = await repo.list_by_conversation(
#             conversation_id=conversation_id,
#             limit=10,
#             offset=0
#         )
#         # Формирование сообщения для OpenRouter API
#         messages = []
#         for msg in history:
#             role = "assistant" if msg.sender_type.value == "assistant" else "user"
#             messages.append({"role": role, "content": msg.content})
#
#         # Добавляем текущее сообщение пользователя (если его ещё нет в истории)
#         if not messages or messages[-1]["role"] != "user":
#             messages.append({"role": "user", "content": content})


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
        message_id: UUID,
        conversation_id: UUID,
        user_id: str,
        content: str,
        idempotency_key: str,
        temperature: float = 0.7,
) -> dict:
    """
    Асинхронная задача: отправка запроса к LLM и обработка ответа.

    :param message_id: UUID сообщения-запроса.
    :param conversation_id: UUID диалога.
    :param user_id: Идентификатор пользователя из Auth Service.
    :param content: Текст сообщения пользователя.
    :param idempotency_key: Уникальный ключ для предотвращения дубликатов.
    :param temperature: Параметр креативности модели.

    :return: dict с результатом обработки.

    :raises: Celery Retry при временных ошибках,
             или возврат dict с error при критических сбоях.
    """
    if err_msg := await _check_rate_limit(user_id, message_id):
        return err_msg.to_dict()

    if err_msg := await _acquire_lock(idempotency_key, message_id):
        return err_msg.to_dict()

    if err_msg := await _check_race_condition(
            self, message_id, idempotency_key
    ):
        return err_msg.to_dict()

    try:


        return {
            "status": "success",
            "message_id": message_id,
            "response_id": assistant_id,
            "content": llm_response,
            "task_id": self.request.id,
        }

    except Exception as exc:
        # -----------------------------------------------------------------
        # Обработка ошибок
        # -----------------------------------------------------------------
        logger.error(
            f"LLM task failed: msg_id={message_id}, "
            f"task_id={self.request.id}, error={exc}",
            exc_info=True
        )

        # Обновляем статус сообщения → FAILED
        try:
            await _update_message_status(
                message_id=msg_uuid,
                new_status=MessageStatus.FAILED,
                metadata={
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                    "task_id": self.request.id,
                }
            )
        except Exception as db_err:
            logger.error(f"Failed to update message status: {db_err}")

        # Решаем, нужно ли повторять задачу
        if isinstance(exc, (ConnectionError, TimeoutError)):
            # Временные ошибки сети — можно повторить
            raise self.retry(exc=exc, countdown=5 * (self.request.retries + 1))
        elif "rate_limit" in str(exc).lower():
            # Rate limit от OpenRouter — ждём дольше
            raise self.retry(exc=exc, countdown=30)
        else:
            # Критическая ошибка — не повторяем, возвращаем ошибку
            return {
                "status": "error",
                "message_id": message_id,
                "error": str(exc),
                "error_type": type(exc).__name__,
                "task_id": self.request.id,
            }

    finally:
        # -----------------------------------------------------------------
        # Освобождение блокировки (всегда)
        # -----------------------------------------------------------------
        try:
            await _release_lock(idempotency_key)
        except Exception as e:
            logger.warning(f"Failed to release lock {idempotency_key}: {e}")


# =============================================================================
# Celery Task: фоновая задача обновления статуса "прочитано"
# =============================================================================

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