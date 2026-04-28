from uuid import UUID

from .base import AppException


class ChatApiClientException(AppException):
    """Ошибка при работе с API чата."""
    pass


class ConversationException(ChatApiClientException):
    """Ошибка при работе с диалогами."""
    pass


class ListConversationsException(ConversationException):
    """Ошибка при получении списка диалогов."""
    pass


class CreateConversationException(ConversationException):
    """Ошибка при создании диалога."""
    def __init__(self, message: str, conversation_title: str):
        super().__init__(message, conversation_title=conversation_title)


class ConversationHistoryException(ConversationException):
    """Ошибка при получении истории диалога."""
    def __init__(self, message: str, conversation_id: UUID):
        super().__init__(message, conversation_id=conversation_id)


class ConversationAccessException(ConversationException):
    """Доступ к диалогу запрещен."""
    def __init__(self, message: str, conversation_id: UUID):
        super().__init__(message, conversation_id=conversation_id)
