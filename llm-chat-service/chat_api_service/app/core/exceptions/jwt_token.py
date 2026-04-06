from .base import AppException


class JWTTokenException(AppException):
    """Ошибка при работе с токеном."""
    pass


class JWTTokenExpired(JWTTokenException):
    """Ошибка валидации токена с истекшим сроком жизни."""


class JWTTokenInvalid(JWTTokenException):
    """Ошибка невалидного токена."""
