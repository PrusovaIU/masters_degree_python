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
from chat_api_service.app.schemas.llm_tasks import LLMTaskStatusSchema, MessageSchema
from chat_api_service.app.consts.message import SenderType
import loguru
from chat_api_service.app.schemas.message import MessageCreate


class ChatUseCase:
    def __init__(
            self,
            message_repository: MessageRepository,
            openrouter_client: OpenRouterClient,
            logger = None
    ):
        self._repo = message_repository
        self._openrouter_client = openrouter_client
        self._logger = logger if logger else loguru.logger

    async def _update_message_status(
            self,
            message_id: UUID,
            new_status: MessageStatus,
            content: str | None = None,
            metadata: dict | None = None,
    ) -> None:
        """
        Обновление статуса и данных сообщения в БД.

        :param message_id: UUID сообщения.
        :param new_status: Новый статус.
        :param content: Опционально новый контент (ответ LLM).
        :param metadata: Опционально метаданные (токены, модель, и т.д.).
        """
        if content is not None or metadata is not None:
            await self._repo.update_content_and_metadata(
                message_id=message_id,
                content=content,
                metadata=metadata,
            )
        await self._repo.update_status(
            message_id=message_id,
            new_status=new_status,
        )

    async def _check_rate_limit(
            self,
            user_id: str,
            message_id: UUID
    ) -> LLMTaskStatusSchema | None:
        """
        Проверка на превышение лимита запросов.

        :param user_id: Идентификатор пользователя из Auth Service.
        :param message_id: UUID сообщения-запроса.
        :return: Статус ошибки, если превышен лимит, иначе None.
        """
        if not await RedisClient.check_rate_limit(user_id):
            self._logger.warning(
                f"Rate limit было превышено для пользователя {user_id}. "
                f"Ключ: {RedisClient.get_rate_limit_key(user_id)}"
            )
            await self._update_message_status(
                message_id=message_id,
                new_status=MessageStatus.FAILED,
                metadata={"error": "rate_limit_exceeded"}
            )
            return LLMTaskStatusSchema(
                status=LLMTasksStatus.RATE_LIMITED,
                message_id=message_id,
                retry_after=settings.redis.rate_limit.llm_window
            )
        return None

    async def _acquire_lock(
            self,
            idempotency_key: str,
            message_id: UUID
    ) -> LLMTaskStatusSchema | None:
        """
        Захват блокировки для предотвращения дубликатов.

        :param idempotency_key: Ключ для идентификации запроса.
        :param message_id: ID сообщения.
        :return: Статус ошибки, если блокировка уже занята, иначе None.
        """
        lock_acquired = await RedisClient.acquire_lock(idempotency_key)
        if not lock_acquired:
            # Блокировка уже занята. Возможно, запрос уже обрабатывается.
            # Проверка на уже обработанный запрос:
            existing: Message | None = \
                await self._repo.get_by_idempotency_key(idempotency_key)

            if existing and existing.status in (
                    MessageStatus.DELIVERED, MessageStatus.READ
            ):
                self._logger.info(
                    f"Идемпотентный запрос уже обработан: {idempotency_key}"
                )
                return LLMTaskStatusSchema(
                    status=LLMTasksStatus.ALREADY_PROCESSED,
                    message_id=message_id,
                    content=existing.content
                )
            else:
                return LLMTaskStatusSchema(
                    status=LLMTasksStatus.PROCESSING,
                    message_id=message_id,
                    note="Request is being processed by another worker"
                )
        return None

    async def _check_race_condition(
            self,
            task: Task,
            message_id: UUID,
            idempotency_key: str
    ) -> LLMTaskStatusSchema | None:
        """
        Проверка на race condition при обработке запроса.

        :param task: Задача Celery.
        :param message_id: ID сообщения.
        :param idempotency_key: Ключ для идентификации запроса.
        :return: Статус ошибки, если запрос уже обрабатывается, иначе None.
        """
        existing_msg = await self._repo.get_by_idempotency_key(idempotency_key)
        if existing_msg:
            if existing_msg.status in (
                    MessageStatus.DELIVERED, MessageStatus.READ
            ):
                self._logger.info(
                    f"Обнаружено дублирование запроса: {idempotency_key}"
                )
                return LLMTaskStatusSchema(
                    status=LLMTasksStatus.CACHED,
                    message_id=str(existing_msg.id),
                    content=existing_msg.content
                )
            elif existing_msg.status == MessageStatus.PROCESSING:
                return LLMTaskStatusSchema(
                    status=LLMTasksStatus.PROCESSING,
                    message_id=message_id
                )
        await self._repo.update_status(message_id, MessageStatus.PROCESSING)
        await self._repo.update_llm_task_id(message_id, task.request.id)
        return None

    async def _prepare_context(
            self,
            conversation_id: UUID,
            content: str
    ) -> list[dict[str, str]]:
        # Получение последних сообщений для контекста
        history = await self._repo.list_by_conversation(
            conversation_id=conversation_id,
            limit=10,
            offset=0
        )
        # Формирование сообщения для OpenRouter API
        messages = []
        for msg in history:
            role = msg.sender_type
            messages.append(MessageSchema(role=role, content=msg.content))

        if not messages or messages[-1]["role"] != "user":
            messages.append(
                MessageSchema(role=SenderType.USER, content=content)
            )
        return [msg.model_dump() for msg in messages]

    async def _handle_llm_response(
            self,
            task: Task,
            response: str,
            message_id: UUID,
            conversation_id: UUID,
            temperature: float,
            idempotency_key: str
    ) -> UUID:
        """
        Обработка ответа LLM и сохранение сообщения в БД.

        :param task: Задача Celery.
        :param response: Ответ LLM.
        :param message_id: ID сообщения.
        :param conversation_id: ID диалога.
        :param temperature: Параметр креативности.
        :param idempotency_key: Ключ для идентификации запроса.
        :return: ID созданного сообщения.
        """
        assistant_message = await self._repo.create(
            conversation_id=conversation_id,
            message_in=MessageCreate(
                sender_type=SenderType.ASSISTANT,
                content=response,
                status=MessageStatus.DELIVERED,
                metadata={
                    "temperature": temperature,
                    "task_id": task.request.id,
                    "tokens_estimated": len(response.split()),
                }
            ),
            idempotency_key=f"{idempotency_key}:response",
        )

        await self._repo.update_status(message_id, MessageStatus.DELIVERED)

        return str(assistant_message.id)

    async def new_message(
            self,
            task: Task,
            message_id: UUID,
            conversation_id: UUID,
            user_id: str,
            content: str,
            idempotency_key: str,
            temperature: float = 0.7
    ):
        if err_msg := await self._check_rate_limit(user_id, message_id):
            return err_msg.to_dict()

        if err_msg := await self._acquire_lock(idempotency_key, message_id):
            return err_msg.to_dict()

        if err_msg := await self._check_race_condition(
                task, message_id, idempotency_key
        ):
            return err_msg.to_dict()

        try:
            messages = await self._prepare_context(conversation_id, content)
            llm_response: str = await self._openrouter_client.chat_completion(
                messages=messages,
                temperature=temperature
            )
            assistant_id = await self._handle_llm_response(
                task,
                llm_response,
                message_id,
                conversation_id,
                temperature,
                idempotency_key
            )
            self._logger.info(
                f"Запрос к LLM обработан успешно: msg_id={message_id}, "
                f"response_id={assistant_id}, task_id={task.request.id}""
            )
        except Exception as err:
            self._logger.error(
                f"Ошибка при обработке запроса к LLM - "
                f"{err} ({err.__class__.__name__}): "
                f"msg_id={message_id}, task_id={task.request.id}, error={err}"
            )

