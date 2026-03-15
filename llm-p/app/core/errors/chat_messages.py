"""Исключения для работы с репозиторием ChatMessages"""
from .base import AppException


class ChatMessagesException(AppException):
    """Базовый класс исключения"""
    pass


class CreateMessageException(ChatMessagesException):
    """Исключение при создании сообщения"""
    pass


class DeleteMessageException(ChatMessagesException):
    """Исключение при удалении сообщения"""
    pass
