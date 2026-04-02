from enum import Enum


class UserRole(str, Enum):
    """Роли пользователей в системе."""
    USER = "user"
    ADMIN = "admin"
    SERVICE = "service"
