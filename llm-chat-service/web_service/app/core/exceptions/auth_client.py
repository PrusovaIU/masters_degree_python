from .base import AppException


class AuthClientError(AppException):
    """Ошибка при работе с сервисом авторизации."""
    pass


class AuthClientUserError(AuthClientError):
    def __init__(self, message: str, user_name: str, **kwargs):
        super().__init__(message, user_name=user_name, **kwargs)


class RegisterError(AuthClientUserError):
    """Ошибка при регистрации нового пользователя."""
    pass


class LoginError(AuthClientUserError):
    """Ошибка при авторизации пользователя."""
    pass


class RefreshTokenError(AuthClientError):
    """Ошибка при обновлении токена."""
    pass


class ProfileError(AuthClientError):
    """Ошибка при получении профиля пользователя."""
    pass
