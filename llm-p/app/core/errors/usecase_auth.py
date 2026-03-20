"""Исключения для usecase авторизации."""
from .base import AppException


class UserAlreadyExistsError(AppException):
    """Пользователь с таким email уже существует."""
    @property
    def message(self) -> str:
        return f"User \"{self._message}\" already exists."


class InvalidCredentialsError(AppException):
    """Неверный email или пароль."""
    pass


class UserNotFoundError(AppException):
    """Пользователь не найден."""
    pass
