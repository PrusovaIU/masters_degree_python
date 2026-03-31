from .security import SecurityError


class TokenError(SecurityError):
    """Ошибка при работе с токеном."""
    pass


class TokenEncodeError(TokenError):
    """Ошибка при кодировании токена."""
    pass
