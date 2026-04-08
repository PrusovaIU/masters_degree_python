from .base import AppException


class UUIDValueError(AppException):
    """Неверный формат UUID."""
    pass
