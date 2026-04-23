from chat_api_service.app.consts.message import MessageStatus, SenderType
from chat_api_service.app.core.idempotency_key import generate_idempotency_key
from chat_api_service.app.db.models import Message
from chat_api_service.app.infra.redis import RedisClient
from chat_api_service.app.repositories.message import MessageRepository
from chat_api_service.app.schemas.llm import LLMQueryResponse, LLMQueryRequest
from chat_api_service.app.consts.llm_tasks import LLMTasksStatus
from chat_api_service.app.schemas.message import MessageCreate
from chat_api_service.app.tasks.llm_tasks import llm_request
from celery.result import AsyncResult
from chat_api_service.app.repositories.conversation import (
    ConversationRepository)


class NewMessageUsecase:
    """
    Usecase для обработки нового сообщения.

    :param message_repository: Репозиторий сообщений.

    :param conversation_repository: Репозиторий диалогов.

    :param user_id: Идентификатор пользователя.

    :param user_request: Запрос пользователя.

    :param custom_idem_key: Пользовательский ключ идемпотентности. Если None,
        то генерируется новый.
    """
    def __init__(
            self,
            message_repository: MessageRepository,
            conversation_repository: ConversationRepository,
            user_id: str,
            user_request: LLMQueryRequest,
            custom_idem_key: str | None
    ):
        self._msg_repository = message_repository
        self._conversation_repository = conversation_repository
        self._user_id = user_id
        self._user_request = user_request
        self._idem_key: str = self._get_idempotency_key(
            user_request, user_id, custom_idem_key
        )

    @staticmethod
    def _get_idempotency_key(
            user_request: LLMQueryRequest,
            user_id: str,
            custom_idem_key: str | None
    ) -> str:
        """
        Получение ключа идемпотентности. Если пользовательский ключ не задан,
        то генерируется новый, иначе используется пользовательский.

        :param user_request: Запрос пользователя.
        :param user_id: Идентификатор пользователя.
        :param custom_idem_key: Пользовательский ключ идемпотентности.
        :return: Ключ идемпотентности.
        """
        if custom_idem_key:
            idempotency_key = custom_idem_key
        else:
            idempotency_key = generate_idempotency_key(
                user_id=user_id,
                conversation_id=user_request.conversation_id,
                content=user_request.content
            )
        return idempotency_key

    async def execute(self) -> LLMQueryResponse:
        """
        Обработка нового сообщения.

        :return: Статус сообщения.

        :raises ConversationNotFound: Диалог не найден.
        :raises ConversationAccessDenied: Доступ запрещен.
        """
        cached_response: LLMQueryResponse | None = \
            await self._check_idempotency_cache()
        if cached_response:
            return cached_response
        cache_response: LLMQueryResponse | None = \
            await self._check_idempotency_msg()
        if cache_response:
            return cache_response
        return await self._create_new_message()

    async def _check_idempotency_cache(self) -> LLMQueryResponse | None:
        """
        Проверка кэша идемпотентности. Если ключ найден, возвращается ответ из
        кэша.

        :return: Закэшированный ответ или None.
        """
        cache: dict | None = await RedisClient.check_idempotency(
            self._idem_key
        )
        return LLMQueryResponse(**cache) if cache else None

    async def _check_idempotency_msg(self) -> LLMQueryResponse | None:
        """
        Проверка существования сообщения с указанным ключом идемпотентности в
        БД.

        :return: Ответ от LLM, если сообщение уже обработано, иначе None.
        """
        response: LLMQueryResponse | None = None
        existing_message: Message | None = \
            await self._msg_repository.get_by_idempotency_key(self._idem_key)
        if existing_message:
            match existing_message.status:
                case MessageStatus.DELIVERED | MessageStatus.READ:
                    # Сообщение уже обработано:
                    response = LLMQueryResponse(
                        message_id=existing_message.id,
                        task_id=existing_message.llm_task_id,
                        status=LLMTasksStatus.CACHED,
                        conversation_id=self._user_request.conversation_id,
                    )
                    await RedisClient.cache_idempotency_result(
                        self._idem_key,
                        response.model_dump()
                    )
                case MessageStatus.PROCESSING:
                    # Сообщение еще обрабатывается:
                    response = LLMQueryResponse(
                        message_id=existing_message.id,
                        task_id=existing_message.llm_task_id,
                        status=LLMQueryResponse.PROCESSING,
                        conversation_id=self._user_request.conversation_id,
                        note="Request is being processed",
                    )
        return response

    async def _create_new_message(self) -> LLMQueryResponse:
        """
        Создание нового сообщения.

        :return: Статус сообщения.

        :raises ConversationNotFound: Диалог не найден.
        :raises ConversationAccessDenied: Доступ запрещен.
        """
        # проверка доступа к диалогу:
        await self._conversation_repository.get(
            self._user_request.conversation_id,
            self._user_id
        )
        user_message: Message = await self._msg_repository.create(
            conversation_id=self._user_request.conversation_id,
            message_in=MessageCreate(
                sender_type=SenderType.USER,
                content=self._user_request.content,
                status=MessageStatus.SENT
            ),
            idempotency_key=self._idem_key
        )
        task: AsyncResult = llm_request.delay(
            message_id=str(user_message.id),
            conversation_id=str(self._user_request.conversation_id),
            user_id=self._user_id,
            content=self._user_request.content,
            idempotency_key=self._idem_key,
            temperature=self._user_request.temperature
        )
        await self._msg_repository.update_llm_task_id(user_message.id, task.id)
        return LLMQueryResponse(
            message_id=user_message.id,
            task_id=task.id,
            status=LLMTasksStatus.QUEUED,
            conversation_id=self._user_request.conversation_id
        )
