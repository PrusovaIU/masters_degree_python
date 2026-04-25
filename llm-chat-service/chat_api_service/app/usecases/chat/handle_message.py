from uuid import UUID

from celery import Task

from chat_api_service.app.consts.message import MessageStatus
from chat_api_service.app.db.models import Message
from chat_api_service.app.infra.redis import RedisClient
from chat_api_service.app.repositories.message import MessageRepository
from chat_api_service.app.services.openrouter_client import OpenRouterClient
from chat_api_service.app.schemas.llm_tasks import MessageSchema
from chat_api_service.app.consts.message import SenderType
import loguru
from chat_api_service.app.schemas.message import MessageCreate
from chat_api_service.app.core.exceptions import chat_new_message as errors
from chat_api_service.app.infra.rabbitmq import RabbitMQClient
from chat_api_service.app.schemas.rabbit_mq import RabbitMQMessageStatus


class ChatNewMessageUsecase:
    def __init__(
            self,
            message_repository: MessageRepository,
            openrouter_client: OpenRouterClient,
            task: Task,
            message_id: UUID,
            conversation_id: UUID,
            user_id: str,
            content: str,
            idempotency_key: str,
            rabbitmq_exchange: str,
            temperature: float = 0.7,
            logger = None
    ):
        self._repo = message_repository
        self._openrouter_client = openrouter_client
        self._task = task
        self._message_id = message_id
        self._conversation_id = conversation_id
        self._user_id = user_id
        self._content = content
        self._idempotency_key = idempotency_key
        self._temperature = temperature
        self._rabbitmq_exchange = rabbitmq_exchange
        self._logger = logger if logger else loguru.logger

    async def _update_message_status(
            self,
            message_id: UUID,
            new_status: MessageStatus | str,
            content: str | None = None,
            metadata: dict | None = None,
    ) -> None:
        """
        Обновление статуса и данных сообщения в БД.

        :param new_status: Новый статус.
        :param content: Опционально новый контент (ответ LLM).
        :param metadata: Опционально метаданные (токены, модель, и т.д.).
        """
        if content is not None or metadata is not None:
            await self._repo.update_content_and_metadata(
                message_id=self._message_id,
                content=content,
                metadata=metadata,
            )
        await self._repo.update_status(
            message_id=message_id,
            new_status=new_status,
        )

    async def _check_rate_limit(self) -> None:
        """
        Проверка на превышение лимита запросов.

        :return: None.

        :raises RateLimitExceededError: Если лимит запросов превышен.
        """
        self._logger.info(f"Проверка лимита для пользователя {self._user_id}")
        if not await RedisClient.check_rate_limit(self._user_id):
            self._logger.warning(
                f"Rate limit было превышено для пользователя {self._user_id}. "
                f"Ключ: {RedisClient.get_rate_limit_key(self._user_id)}"
            )
            await self._update_message_status(
                new_status=MessageStatus.FAILED,
                metadata={"error": "rate_limit_exceeded"}
            )
            raise errors.RateLimitExceededError("Rate limit exceeded")

    async def _acquire_lock(self) -> None:
        """
        Захват блокировки для предотвращения дубликатов.

        :return: None.

        :raises AlreadyProcessedError: Если запрос уже обработан.
        :raises IsProcessingError: Если запрос уже обрабатывается.
        """
        self._logger.info(f"Захват блокировки для {self._idempotency_key}")
        lock_acquired = await RedisClient.acquire_lock(self._idempotency_key)
        if not lock_acquired:
            # Блокировка уже занята. Возможно, запрос уже обрабатывается.
            # Проверка на уже обработанный запрос:
            existing: Message | None = \
                await self._repo.get_by_idempotency_key(self._idempotency_key)

            if existing and existing.status in (
                    MessageStatus.DELIVERED, MessageStatus.READ
            ):
                self._logger.info(
                    f"Идемпотентный запрос уже обработан: "
                    f"{self._idempotency_key}"
                )
                raise errors.AlreadyProcessedError(
                    "Запрос уже обработан",
                    existing.content
                )
            else:
                raise errors.IsProcessingError("Запрос уже обрабатывается")
        return None

    async def _check_race_condition(self) -> None:
        """
        Проверка на race condition при обработке запроса.

        :return: None.

        :raises CachedError: Если запрос уже закэширован.
        :raises IsProcessingError: Если запрос уже обрабатывается.
        """
        self._logger.info(f"Проверка race condition для {self._message_id}")
        existing_msg = await self._repo.get_by_idempotency_key(
            self._idempotency_key
        )
        if existing_msg:
            if existing_msg.status in (
                    MessageStatus.DELIVERED, MessageStatus.READ
            ):
                self._logger.info(
                    f"Обнаружено дублирование запроса: {self._idempotency_key}"
                )
                raise errors.CachedError(
                    "Запрос закэширован",
                    existing_msg.content
                )
            elif existing_msg.status == MessageStatus.PROCESSING:
                raise errors.IsProcessingError("Запрос уже обрабатывается")

        await self._repo.update_status(
            self._message_id, MessageStatus.PROCESSING
        )
        await self._repo.update_llm_task_id(
            self._message_id, self._task.request.id
        )
        return None

    async def _prepare_context(self) -> list[dict[str, str]]:
        """
        Подготовка контекста для запроса к LLM.

        :return: Список сообщений с контекстом для LLM.
        """
        self._logger.info(f"Подготовка контекста для {self._message_id}")
        # Получение последних сообщений для контекста
        history = await self._repo.list_by_conversation(
            conversation_id=self._conversation_id,
            limit=10,
            offset=0
        )
        history = [
            _msg for _msg in history if _msg.status != MessageStatus.FAILED
        ]
        # Формирование сообщения для OpenRouter API
        messages = []
        for msg in reversed(history):
            role = msg.sender_type.value
            messages.append(MessageSchema(role=role, content=msg.content))

        return [msg.model_dump() for msg in messages]

    async def _handle_llm_response(self, response: str) -> UUID:
        """
        Обработка ответа LLM и сохранение сообщения в БД.

        :param response: Ответ LLM.
        :return: ID созданного сообщения.
        """
        self._logger.info(f"Обработка ответа LLM для {self._message_id}")
        assistant_message = await self._repo.create(
            conversation_id=self._conversation_id,
            message_in=MessageCreate(
                sender_type=SenderType.ASSISTANT,
                content=response,
                status=MessageStatus.PROCESSING,
                metadata={
                    "temperature": self._temperature,
                    "task_id": self._task.request.id,
                    "tokens_estimated": len(response.split()),
                }
            ),
            idempotency_key=f"{self._idempotency_key}:response",
        )
        return assistant_message.id

    async def _handle_error(
            self,
            exc: Exception,
            assistant_msg_id: UUID | None
    ) -> None:
        """
        Обработка ошибок при выполнении запроса к LLM.

        :param exc: Возникшее исключение.
        :return: Статус задачи с ошибкой.

        :raises Exception: Перенаправление исключения exc.
        """
        try:
            await self._update_message_status(
                self._message_id,
                new_status=MessageStatus.FAILED,
                metadata={
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                    "task_id": self._task.request.id,
                }
            )
            if assistant_msg_id:
                await self._update_message_status(
                    assistant_msg_id,
                    new_status=MessageStatus.FAILED,
                    metadata={
                        "error": str(exc),
                        "error_type": type(exc).__name__,
                        "task_id": self._task.request.id,
                    }
                )
        except Exception as db_err:
            self._logger.error(
                f"Не удалось обновить статус сообщения: {db_err} "
                f"(message_id={self._message_id})"
            )
        finally:
            raise exc

    async def _release_lock(self) -> None:
        """
        Освобождение блокировки после завершения запроса.

        :return: None.
        """
        self._logger.info(
            f"Освобождение блокировки для {self._idempotency_key}"
        )
        try:
            await RedisClient.release_lock(self._idempotency_key)
        except Exception as err:
            self._logger.warning(
                f"Не удалось освободить блокировку: "
                f"task_id={self._task.request.id}, "
                f"message_id={self._message_id}, "
                f"idempotency_key={self._idempotency_key} "
                f"{err} ({err.__class__.__name__})"
            )

    async def _rabbbitmq_publish(self) -> None:
        """
        Публикация сообщения в RabbitMQ.

        :return: None.
        """
        message_status = RabbitMQMessageStatus(
            message_id=self._message_id,
            conversation_id=self._conversation_id,
            user_id=self._user_id
        )
        await RabbitMQClient.publish(
            message_status.model_dump_json().encode("utf-8"),
            self._rabbitmq_exchange
        )

    async def _change_status(self, assistant_message_id: UUID) -> None:
        """
        Изменение статуса сообщения в БД на "delivered".

        :param assistant_message_id: Идентификатор сообщения с ответом LLM.
        :return: None.
        """
        await self._repo.update_status(
            self._message_id, MessageStatus.DELIVERED
        )
        await self._repo.update_status(
            assistant_message_id, MessageStatus.DELIVERED
        )

    async def new_message(self) -> tuple[UUID, str]:
        """
        Обработка нового сообщения от пользователя.
        :return: ID созданного сообщения и ответ LLM.

        :raises RateLimitExceededError: Если превышен лимит запросов.
        :raises AlreadyProcessedError: Если запрос уже обработан.
        :raises IsProcessingError: Если запрос уже обрабатывается.
        :raises CachedError: Если запрос закэширован.
        """
        await self._check_rate_limit()
        await self._acquire_lock()
        await self._check_race_condition()
        assistant_msg_id: UUID | None = None
        try:
            messages = await self._prepare_context()
            llm_response: str = await self._openrouter_client.call_openrouter(
                messages=messages,
                temperature=self._temperature
            )
            assistant_msg_id = await self._handle_llm_response(llm_response)
            self._logger.info(
                f"Запрос к LLM обработан успешно: msg_id={self._message_id}, "
                f"response_id={assistant_msg_id}, "
                f"task_id={self._task.request.id}"
            )
            await self._rabbbitmq_publish()
        except Exception as err:
            self._logger.error(
                f"Ошибка при обработке запроса к LLM - "
                f"{err} ({err.__class__.__name__}): "
                f"msg_id={self._message_id}, task_id={self._task.request.id}"
            )
            await self._handle_error(err, assistant_msg_id)
        else:
            await self._change_status(assistant_msg_id)
        finally:
            await self._release_lock()
        return assistant_msg_id, llm_response
