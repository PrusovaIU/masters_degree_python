from .security import SecurityError


class PasswordHashError(SecurityError):
    """Ошибка при хешировании или проверке пароля."""
    pass


class VerifyPasswordError(SecurityError):
    """Ошибка при проверке пароля."""
    pass


class HashFormatError(VerifyPasswordError):
    """Ошибка формата хеша."""
    pass
