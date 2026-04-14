from uuid import UUID

from loguru import logger

from chat_api_service.app.repositories.conversation import \
    ConversationRepository
from chat_api_service.app.repositories.message import MessageRepository
from chat_api_service.app.schemas.message import MessageResponse
from chat_api_service.app.schemas.conversation import \
    ConversationHistoryParams, ConversationHistoryResponse, PaginationMeta


class ChatHistoryUsecase:
    """
    Usecase для получения истории сообщений диалога.

    :param conversation_repo: Репозиторий для работы с диалогами.
    :param message_repo: Репозиторий для работы с сообщениями.
    """
    def __init__(
            self,
            conversation_repo: ConversationRepository,
            message_repo: MessageRepository
    ):
        self._conv_repo = conversation_repo
        self._msg_repo = message_repo

    async def get_history(
            self,
            conversation_id: UUID,
            user_id: str,
            params: ConversationHistoryParams
    ) -> ConversationHistoryResponse:
        """
        Получение истории сообщений диалога.

        :param conversation_id: UUID диалога.
        :param user_id: Идентификатор пользователя из Auth Service.
        :param params: Параметры пагинации и фильтрации.

        :return: Схема ответа с сообщениями и метаданными пагинации.

        :raises ConversationNotFound: Если диалог не существует.

        :raises ConversationAccessDenied: Если диалог не принадлежит
            пользователю.

        :raises InvalidPaginationParams: Если параметры пагинации некорректны.
        """
        conversation = await self._conv_repo.get(conversation_id, user_id)

        messages = await self._msg_repo.list_by_conversation(
            conversation_id=conversation_id,
            limit=params.limit,
            offset=params.offset
        )

        total_count = await self._msg_repo.count_by_conversation(
            conversation_id=conversation_id
        )

        message_responses = [
            MessageResponse.model_validate(msg, from_attributes=True)
            for msg in messages
        ]

        logger.info(
            f"Информация о диалоге: {conversation}",
            conversation_id=str(conversation_id),
            user_id=user_id,
            messages_count=len(message_responses),
            limit=params.limit,
            offset=params.offset,
        )

        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            conversation_title=conversation.title,
            messages=message_responses,
            pagination=PaginationMeta(
                limit=params.limit,
                offset=params.offset,
                total=total_count
            )
        )
