from starlette import status

from libs.base_exception import AppException


class SecurityError(AppException):
    """Базовое исключение для ошибок безопасности."""
    pass


class AuthError(SecurityError):
    """Ошибка аутентификации."""
    @property
    def exc_status_code(self) -> int:
        return status.HTTP_401_UNAUTHORIZED


class InvalidCredentialsError(AuthError):
    """Неверные учетные данные."""
    def __init__(self):
        super().__init__("Неверный логин или пароль.")


class PermissionDeniedError(SecurityError):
    @property
    def exc_status_code(self) -> int:
        return status.HTTP_403_FORBIDDEN
