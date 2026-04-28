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


class ConversationWithIDException(ConversationException):
    def __init__(self, message: str, conversation_id: UUID):
        super().__init__(message, conversation_id=conversation_id)


class ConversationHistoryException(ConversationException):
    """Ошибка при получении истории диалога."""
    def __init__(self, message: str, conversation_id: UUID):
        super().__init__(message, conversation_id=conversation_id)


class ConversationAccessException(ConversationWithIDException):
    """Доступ к диалогу запрещен."""
    pass


class ConversationNotFoundException(ConversationWithIDException):
    """Диалог не найден."""
    pass


class LLMQueryException(ChatApiClientException):
    """Ошибка при запросе к LLM."""
    def __init__(
            self,
            message: str,
            conversation_id: UUID,
            content: str
    ):
        super().__init__(
            message,
            conversation_id=conversation_id,
            content=content
        )
