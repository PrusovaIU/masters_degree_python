from datetime import timedelta
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, BaseModel


class OpenRouterSettings(BaseModel):
    """
    Схема настроек OpenRouter
    """
    api_key: Optional[str] = Field(
        description="API ключ для OpenRouter"
    )
    base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="Базовый URL OpenRouter API"
    )
    model: str = Field(
        default="stepfun/step-3.5-flash:free",
        description="Модель OpenRouter по умолчанию"
    )
    site_url: str
    app_name: Optional[str] = Field(
        default="llm-fastapi-openrouter",
        description="Заголовок приложения для OpenRouter"
    )
    referer: Optional[str] = Field()
    request_timeout: int = Field(
        default=10,
        description="Таймаут запроса в секундах"
    )


class PasswordSettings(BaseModel):
    """
    Схема настроек хэширования пароля
    """
    pbkdf2_iterations: int = Field(
        default=600000,
        description="Количество итераций для PBKDF2"
    )
    salt_len: int = Field(
        default=32,
        description="Длина соли в байтах"
    )
    hash_len: int = Field(
        default=32,
        description="Длина выходного хеша в байтах"
    )


class JWTSettings(BaseModel):
    secret: str = Field(description="Путь к ключу для JWT")
    alg: str = Field(
        default="HS256",
        description="Алгоритм подписи JWT токенов"
    )
    access_token_expire_minutes: int = Field(
        default=60,
        description="Время жизни access token в минутах"
    )

    @property
    def access_token_expires(self) -> timedelta:
        return timedelta(minutes=self.access_token_expire_minutes)


class CORSSettings(BaseModel):
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
    Конфигурация приложения
    Все настройки загружаются из переменных окружения или файла .env
    """

    # Общие настройки приложения
    app_name: str = Field(
        default="llm-p",
        description="Название приложения"
    )

    env: str = Field(
        default="local",
        description="Текущее окружение"
    )

    jwt: JWTSettings

    # Настройки базы данных
    sqlite_path: str = Field(
        default="./app.db",
        description="Путь к файлу SQLite базы данных"
    )

    openrouter: OpenRouterSettings
    password: Optional[PasswordSettings] = Field(
        description="Параметры хэширования пароля",
        default_factory=PasswordSettings
    )
    cors: CORSSettings = Field(
        default_factory=CORSSettings,
        description="Настройки CORS"
    )

    model_config = SettingsConfigDict(
        env_file="/home/hex/git/masters_degree_python/llm-p/.env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__"
    )

    @property
    def database_url(self) -> str:
        """
        Формирует URL для подключения к SQLite
        """
        return f"sqlite+aiosqlite:///{self.sqlite_path}"


settings = Settings()
