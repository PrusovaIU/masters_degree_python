from enum import Enum


class TokenDataKeys(str, Enum):
    """Ключи данных в токене"""
    SUB = "sub"
    ROLE = "role"
    EXP = "exp"
    IAT = "iat"
