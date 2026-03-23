from enum import Enum


class Roles(str, Enum):
    """Названия ролей"""
    admin = "admin"
    user = "user"
    assistant = "assistant"
    system = "system"
