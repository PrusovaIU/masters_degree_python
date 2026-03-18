"""Исключения для usecase чата."""
from .base import AppException


class ChatUseCaseError(AppException):
    """Базовое исключение для ошибок чата."""
    pass
