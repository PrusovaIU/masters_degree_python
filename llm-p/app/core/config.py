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
    base_sql: str = Field(
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


class Settings(BaseSettings):
    """
    Конфигурация приложения
    Все настройки загружаются из переменных окружения или файла .env
    """

    # Общие настройки приложения
    app_name: str = Field(
        # default="llm-p",
        description="Название приложения"
    )

    # Настройки JWT
    jwt_secret: str = Field(description="Путь к секретному ключу для JWT")
    jwt_alg: str = Field(
        default="HS256",
        description="Алгоритм подписи JWT токенов"
    )
    access_token_expire_minutes: int = Field(
        default=60,
        description="Время жизни access token в минутах"
    )

    # Настройки базы данных
    sqlite_path: str = Field(
        default="./app.db",
        description="Путь к файлу SQLite базы данных"
    )

    openrouter: OpenRouterSettings

    model_config = SettingsConfigDict(
        env_file=".env",
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


settings = Settings(_env_file="/home/hex/git/masters_degree_python/llm-p/.env")
