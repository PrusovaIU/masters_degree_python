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
    pass


class GetConversationException(ConversationException):
    """Ошибка при получении диалога."""
    pass


class AccessException(AppException):
    """Доступ к объекту запрещен."""
    def __init__(self, message: str, _id: UUID | None):
        super().__init__(message, id=_id)


class ConversationNotFoundException(ConversationWithIDException):
    """Диалог не найден."""
    pass


class MessageException(ChatApiClientException):
    def __init__(self, message: str, message_id: UUID):
        super().__init__(message, message_id=message_id)


class MessageNotFoundException(MessageException):
    """Сообщение не найдено."""
    pass


class GetMessageException(MessageException):
    """Ошибка при получении сообщения."""
    pass


class ChangeMessageStatusException(MessageException):
    """Ошибка при изменении статуса сообщения."""
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


class GetTaskStatusException(ChatApiClientException):
    """Ошибка при получении статуса задачи."""
    pass


class TaskNotFoundException(ChatApiClientException):
    """Задача не найдена."""
    def __init__(self, message: str, task_id: UUID):
        super().__init__(message, task_id=task_id)
