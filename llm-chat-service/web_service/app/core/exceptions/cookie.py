from .base import AppException

class CookieUnfoundException(AppException):
    """Куки не найдены."""
    def __init__(self, message: str, cookie_name: str):
        super().__init__(message, cookie_name=cookie_name)
