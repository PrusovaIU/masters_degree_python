from .base import AppException


class UserAlreadyExistsError(AppException):
    """Пользователь с таким email уже существует."""
    pass


class InvalidCredentialsError(AppException):
    """Неверный email или пароль."""
    pass


class UserNotFoundError(AppException):
    """Пользователь не найден."""
    pass
