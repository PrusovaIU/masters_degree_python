from .base import AppException


class InvalidMessageStatus(AppException):
    """Ошибка при изменении статуса сообщения."""
    pass
