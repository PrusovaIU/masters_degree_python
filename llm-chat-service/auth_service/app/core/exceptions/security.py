from starlette import status

from .base import AppException


class SecurityError(AppException):
    """Базовое исключение для ошибок безопасности."""
    pass


class AuthError(SecurityError):
    """Ошибка аутентификации."""
    @property
    def status_code(self) -> int:
        return status.HTTP_401_UNAUTHORIZED
