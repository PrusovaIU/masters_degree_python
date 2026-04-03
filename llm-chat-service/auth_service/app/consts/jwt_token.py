from enum import Enum


class TokenDataKeys(str, Enum):
    """Ключи данных в токене"""
    SUB = "sub"
    ROLE = "role"
    EXP = "exp"
    IAT = "iat"


class TokenType(str, Enum):
    """Типы токенов"""
    access = "access"
    refresh = "refresh"
    not_set = "not_set"
