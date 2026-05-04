from .base import AppException


class PasswordNotMatchException(AppException):
    """
    Пароли при регистрации не совпадают
    """
    pass
