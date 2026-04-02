from .security import SecurityError, AuthError


class PasswordHashError(SecurityError):
    """Ошибка при хешировании или проверке пароля."""
    pass


class VerifyPasswordError(AuthError):
    """Ошибка при проверке пароля."""
    pass


class HashFormatError(VerifyPasswordError):
    """Ошибка формата хеша."""
    pass
