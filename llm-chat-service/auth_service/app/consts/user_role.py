from enum import Enum


class UserRole(str, Enum):
    """Роли пользователей в системе."""
    user = "user"
    admin = "admin"
    service = "service"
