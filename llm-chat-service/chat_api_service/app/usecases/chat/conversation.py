from uuid import UUID

from loguru import logger

from chat_api_service.app.db.models import Conversation
from chat_api_service.app.repositories.conversation import \
    ConversationRepository
from chat_api_service.app.repositories.message import MessageRepository
from libs.schemas.message import MessageResponse
from libs.schemas.conversation import \
    ConversationHistoryResponse, ConversationResponse
from libs.schemas.pagination import PaginationMeta


class ConversationUsecase:
    """
    Usecase управления диалогами.

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

    async def create_conversation(
            self,
            user_id: str,
            title: str
    ) -> Conversation:
        """
        Создание диалога.

        :param user_id: Идентификатор диалога.
        :param title: Заголовок диалога.
        :return: Данные диалога.
        """
        conv_data: Conversation = await self._conv_repo.create(
            user_id, title
        )
        logger.success(f"Диалог '{title}' создан для пользователя {user_id}")
        return conv_data

    async def list_conversations(
            self,
            user_id: str | None,
            limit: int,
            offset: int
    ) -> tuple[list[ConversationResponse], int]:
        """
        Получение списка диалогов пользователя, отсортированных по дате
        создания.

        :param user_id: Идентификатор пользователя из Auth Service.
        :param limit: Количество элементов на странице.
        :param offset: Смещение для пагинации.
        :return: Список диалогов с пагинацией, общее количество диалогов.
        """
        conversations, total = await self._conv_repo.list(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
        conversations = [
            ConversationResponse.model_validate(
                conv,
                from_attributes=True
            )
            for conv in conversations
        ]
        return conversations, total

    async def get_history(
            self,
            conversation_id: UUID,
            user_id: str,
            limit: int,
            offset: int
    ) -> ConversationHistoryResponse:
        """
        Получение истории сообщений диалога.

        :param conversation_id: UUID диалога.
        :param user_id: Идентификатор пользователя из Auth Service.
        :param limit: Лимит количества сообщений.
        :param offset: Смещение для пагинации.

        :return: Схема ответа с сообщениями и метаданными пагинации.

        :raises ConversationNotFound: Если диалог не существует.

        :raises ConversationAccessDenied: Если диалог не принадлежит
            пользователю.
        """
        conversation = await self._conv_repo.get(conversation_id, user_id)

        await self._msg_repo.mark_as_read(conversation_id)

        messages = await self._msg_repo.list_by_conversation(
            conversation_id=conversation_id,
            limit=limit,
            offset=offset
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
            limit=limit,
            offset=offset,
        )

        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            conversation_title=conversation.title,
            messages=message_responses,
            pagination=PaginationMeta(
                limit=limit,
                offset=offset,
                total=total_count
            )
        )

    async def get_info(
            self,
            conversation_id: UUID,
            user_id: str
    ) -> Conversation:
        """
        Получение информации о диалоге.

        :param conversation_id: Идентификатор диалога.
        :param user_id: Идентификатор пользователя.
        :return: Данные диалога.

        :raises ConversationNotFound: Если диалог не существует.

        :raises ConversationAccessDenied: Если диалог не принадлежит
            пользователю.
        """
        return await self._conv_repo.get(conversation_id, user_id)
