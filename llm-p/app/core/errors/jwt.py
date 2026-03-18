from .base import AppException


class TokenError(AppException):
    """Ошибка работы с токеном"""
    pass


class TokenVerifyError(TokenError):
    """Ошибка верификации токена"""
    pass


class TokenExpiredError(TokenVerifyError):
    """Ошибка истечения срока действия токена"""
    pass

class CreateTokenError(TokenError):
    """Ошибка создания токена"""
    pass
