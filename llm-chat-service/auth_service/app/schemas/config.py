from datetime import timedelta
from pathlib import Path
from typing import Literal
from urllib.parse import quote_plus

from loguru import logger
from pydantic import BaseModel, Field, PrivateAttr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    def get_secret_files(self):
        """Определение секретного ключа"""
        if self.data:
            self._secret = self.data
        elif self.path:
            self._secret = self._load_secret(self.path)
        else:
            raise ValueError(
                "Не указан секретный ключ JWT (secret_data/secret_path)"
            )

    @property
    def secret(self) -> str:
        return self._secret


class JWTConfig(BaseModel):
    """Настройки JWT"""
    access_secret: JWTSecret = Field(
        description="Секретный ключ для подписи access токенов"
    )
    refresh_secret: JWTSecret = Field(
        description="Секретный ключ для подписи refresh токенов"
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
