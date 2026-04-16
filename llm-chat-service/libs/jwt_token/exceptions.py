from fastapi import status

from libs.base_exception import AppException


class TokenError(AppException):
    """Ошибка при работе с токеном."""
    pass


class TokenEncodeError(TokenError):
    """Ошибка при кодировании токена."""
    pass


class TokenDecodeError(TokenError):
    """Ошибка при декодировании токена."""
    pass


class VerifyTokenError(TokenError):
    """Ошибка при проверке токена."""

    _AUTH_HEADERS = {"WWW-Authenticate": "Bearer"}

    def __init__(self, message: str):
        super().__init__(message, self._AUTH_HEADERS)

    @property
    def exc_status_code(self) -> int:
        return status.HTTP_401_UNAUTHORIZED


class InvalidTokenError(VerifyTokenError):
    """Невалидный токен."""
    pass


class TokenExpiredError(VerifyTokenError):
    """Ошибка при проверке срока действия токена."""
    pass
