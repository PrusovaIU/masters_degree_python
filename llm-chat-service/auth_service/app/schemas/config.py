from datetime import timedelta
from pathlib import Path
from typing import Literal
from urllib.parse import quote_plus

from loguru import logger
from pydantic import BaseModel, Field, PrivateAttr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTConfig(BaseModel):
    """Настройки JWT"""
    access_secret_path: Path = Field(
        description="Путь к файлу с ключом для подписи access токенов"
    )
    refresh_secret_path: Path = Field(
        description="Путь к файлу с ключом для подписи refresh токенов"
    )
    token_type: str = Field(default="bearer", description="Тип токена")
    alg: str = Field(default="HS256", description="Алгоритм подписи JWT")
    access_expire_minutes: int = Field(
        default=15,
        description="Время жизни access токена в минутах",
    )
    refresh_expire_hours: int = Field(
        default=24,
        description="Время жизни refresh токена в часах",
    )

    _access_secret: str | None = PrivateAttr(default=None)
    _refresh_secret: str | None = PrivateAttr(default=None)

    @staticmethod
    def _load_secret(
            path: Path,
            secret_type: Literal["access", "refresh"]
    ) -> str:
        """
        Загрузка секретного ключа из файла.

        :param path: Путь к файлу с ключом.
        :param secret_type: Тип ключа (access или refresh).
        :return: Ключ.

        :raises ValueError: Если файл не найден или не может быть прочитан.
        """
        try:
            return path.read_text(encoding="utf-8").strip()
        except OSError as err:
            err_title = f"Ошибка чтения файла с {secret_type} ключом"
            logger.error(f"{err_title}: {err}")
            raise ValueError(err_title) from err

    @model_validator(mode="after")
    def load_secret_files(self):
        """Загрузка секретных ключей из файлов."""
        self._access_secret = self._load_secret(
            self.access_secret_path, "access"
        )
        self._refresh_secret = self._load_secret(
            self.refresh_secret_path, "refresh"
        )
        return self

    @property
    def access_secret(self) -> str:
        """
        :return: ключ для подписи access токенов.
        """
        return self._access_secret

    @property
    def refresh_secret(self) -> str:
        """
        :return: ключ для подписи refresh токенов.
        """
        return self._refresh_secret

    @property
    def access_expire(self) -> timedelta:
        return timedelta(minutes=self.access_expire_minutes)

    @property
    def access_expire_seconds(self) -> int:
        return int(self.access_expire.total_seconds())

    @property
    def refresh_expire(self) -> timedelta:
        return timedelta(hours=self.refresh_expire_hours)

    @property
    def refresh_expire_seconds(self) -> int:
        return int(self.refresh_expire.total_seconds())


class Database(BaseModel):
    """Настройки базы данных"""
    host: str = Field(description="Хост базы данных")
    port: int = Field(description="Порт базы данных")
    db_name: str = Field(description="Имя базы данных")
    user: str = Field(description="Пользователь базы данных")
    password: str = Field(description="Пароль пользователя базы данных")
    schema: str = Field(default="public", description="Схема базы данных")

    @property
    def database_url(self) -> str:
        """
        :return: строка подключения к базе данных.
        """
        passwd = quote_plus(self.password)
        return (f"postgresql+asyncpg://{self.user}:{passwd}"
                f"@{self.host}:{self.port}/{self.db_name}")


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


class Settings(BaseSettings):
    """
    Настройки приложения, загружаемые из переменных окружения.
    """

    model_config = SettingsConfigDict(
        # env_file=".env",
        env_file="/home/hex/git/masters_degree_python/llm-chat-service/auth_service/.env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__"
    )
    app_name: str = Field(
        default="Auth Service",
        description="Название сервиса"
    )
    env: str = Field(default="prod", description="Окружение выполнения")

    jwt: JWTConfig = Field(description="Настройки JWT")
    db: Database = Field(description="Настройки базы данных")
    cors: CORSSettings = Field(
        default_factory=CORSSettings,
        description="Настройки CORS"
    )
