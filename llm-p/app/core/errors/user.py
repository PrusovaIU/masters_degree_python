"""Исключения для работы с репозиторием User"""
from .base import AppException


class UserException(AppException):
    """Базовый класс исключений"""
    pass


class UserNotFound(UserException):
    """Исключение пробрасывается в случае, если пользователь не найден"""
    pass


class CreateUserError(UserException):
    """
    Исключение пробрасывается в случае, если не удалось создать пользователя
    """
    pass


class UserAlreadyExists(CreateUserError):
    """Исключение пробрасывается в случае, если пользователь уже существует"""
    pass
