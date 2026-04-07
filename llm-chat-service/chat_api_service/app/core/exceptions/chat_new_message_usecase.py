from .base import AppException


class ChatNewMessageError(AppException):
    """Ошибка при создании нового сообщения."""


class RateLimitExceededError(ChatNewMessageError):
    """
    Ошибка превышения лимита сообщений.
    """
    pass


class AlreadyProcessedError(ChatNewMessageError):
    """Сообщение уже обработано."""
    def __init__(self, message: str, content: str):
        super().__init__(message)
        self._content = content

    @property
    def content(self) -> str:
        """Содержимое ответа."""
        return self._content


class IsProcessingError(ChatNewMessageError):
    """Сообщение уже обрабатывается."""
    pass


class CachedError(AlreadyProcessedError):
    """Ошибка при закешированном запросе."""
    pass
