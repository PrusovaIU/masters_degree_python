from .security import SecurityError


class TokenError(SecurityError):
    """Ошибка при работе с токеном."""
    pass


class TokenEncodeError(TokenError):
    """Ошибка при кодировании токена."""
    pass


class TokenDecodeError(TokenError):
    """Ошибка при декодировании токена."""
    pass


class InvalidTokenTypeError(TokenError):
    """Ошибка при проверке типа токена."""
    pass


class TokenExpiredError(TokenError):
    """Ошибка при проверке срока действия токена."""
    pass


class InvalidTokenSignatureError(TokenError):
    """Ошибка при проверке подписи токена."""
    pass
