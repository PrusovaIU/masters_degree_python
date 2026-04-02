from .security import AuthError
from .base import AppException


class TokenError(AppException):
    """Ошибка при работе с токеном."""
    pass


class TokenEncodeError(TokenError):
    """Ошибка при кодировании токена."""
    pass


class TokenDecodeError(TokenError):
    """Ошибка при декодировании токена."""
    pass


class InvalidTokenError(AuthError):
    """Невалидный токен."""
    pass


class TokenExpiredError(AuthError):
    """Ошибка при проверке срока действия токена."""
    pass
