from enum import Enum


class DBType(Enum):
    """Поддерживаемые СУБД"""
    postgres = "postgres"
    sqlite = "sqlite"
