from uuid import UUID

from chat_api_service.app.core.exceptions.chat_history import \
    ChatHistoryException


class ConversationNotFound(ChatHistoryException):
    """
    Диалог не найден.

    :param message: Сообщение об ошибке.
    :param conversation_id: UUID запрошенного диалога.
    """

    def __init__(self, message: str, conversation_id: UUID):
        super().__init__(message, conversation_id=conversation_id)
        self._conversation_id = conversation_id

    @property
    def conversation_id(self) -> UUID:
        return self._conversation_id


class ConversationAccessDenied(ChatHistoryException):
    """
    Доступ к диалогу запрещён.

    :param message: Сообщение об ошибке.
    :param conversation_id: UUID диалога.
    :param user_id: ID пользователя, которому отказано.
    """

    def __init__(self, message: str, conversation_id: UUID, user_id: str):
        super().__init__(
            message,
            conversation_id=conversation_id,
            user_id=user_id
        )
        self._conversation_id = conversation_id
        self._user_id = user_id

    @property
    def conversation_id(self) -> UUID:
        return self._conversation_id

    @property
    def user_id(self) -> str:
        return self._user_id
