from pathlib import Path
from typing import Self, Literal
from urllib.parse import quote_plus

from loguru import logger
from pydantic import BaseModel, Field, PrivateAttr, model_validator

from libs.consts.db import DBType


class JWTSecret(BaseModel):
    """Секретный ключ для подписи JWT"""
    data: str | None = Field(
        default=None,
        description="Секретный ключ для подписи JWT. Если не указан, "
                    "берется из файла secret_path."
    )
    path: Path | None = Field(
        default=None,
        description="Путь к файлу с секретным ключом для подписи JWT."
                    "Если не указан, берется из параметра secret_data."
    )

    _secret: str | None = PrivateAttr(default=None)

    @staticmethod
    def _load_secret(
            path: Path
    ) -> str:
        """
        Загрузка секретного ключа из файла.

        :param path: Путь к файлу с ключом.
        :return: Ключ.

        :raises ValueError: Если файл не найден или не может быть прочитан.
        """
        try:
            return path.read_text(encoding="utf-8").strip()
        except OSError as err:
            err_title = f"Ошибка чтения файла с ключом {path.absolute()}"
            logger.error(f"{err_title}: {err}")
            raise ValueError(err_title) from err

    @model_validator(mode="after")
    def get_secret_files(self) -> Self:
        """Определение секретного ключа"""
        if self.data:
            self._secret = self.data
        elif self.path:
            self._secret = self._load_secret(self.path)
        else:
            raise ValueError(
                "Не указан секретный ключ JWT (secret_data/secret_path)"
            )
        return self

    @property
    def secret(self) -> str:
        return self._secret


class DatabaseConfig(BaseModel):
    """Настройки базы данных"""
    host: str = Field(description="Хост базы данных")
    port: int = Field(description="Порт базы данных")
    db_name: str = Field(description="Имя базы данных")
    user: str = Field(description="Пользователь базы данных")
    password: str = Field(description="Пароль пользователя базы данных")
    db_schema: str = Field(default="public", description="Схема базы данных")
    test_db_path: str | None = Field(
        default=None,
        description="Путь к тестовой базе данных SQLite"
    )
    db_type: DBType = Field(
        default=DBType.postgres,
        description="Тип базы данных"
    )

    _database_url: str = PrivateAttr(default=None)

    @model_validator(mode="after")
    def get_database_url(self) -> Self:
        """Формирование строки подключения к базе данных"""
        if self.db_type is DBType.postgres:
            passwd = quote_plus(self.password)
            self._database_url = \
                (f"postgresql+asyncpg://{self.user}:{passwd}"
                 f"@{self.host}:{self.port}/{self.db_name}")
        elif self.db_type is DBType.sqlite:
            if not self.test_db_path:
                raise ValueError(
                    "Не указан путь к тестовой базе данных SQLite"
                )
            self._database_url = f"sqlite+aiosqlite:///{self.test_db_path}"
        else:
            raise ValueError(
                f"Неподдерживаемый тип базы данных: {self.db_type}"
            )
        return self

    @property
    def database_url(self) -> str:
        """
        :return: строка подключения к базе данных.
        """
        return self._database_url


class CORSSettings(BaseModel):
    """Настройки CORS"""
    enabled: bool = Field(default=True, description="Флаг включения CORS")
    origins: list[str] = Field(
        default=["*"],
        description="Список разрешенных источников"
    )
    methods: list[str] = Field(
        default=["*"],
        description="Список разрешенных методов"
    )
    headers: list[str] = Field(
        default=["*"],
        description="Список разрешенных заголовков"
    )
    credentials: bool = Field(
        default=True,
        description="Разрешить отправку куки"
    )


class LogConfig(BaseModel):
    file_path: str = Field(
        default="logs/auth_service.log",
        description="Путь к файлу логов"
    )
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Уровень логирования"
    )
    rotation: str = Field(
        default="1 day",
        description="Ротация логов"
    )
