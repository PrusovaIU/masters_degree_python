from functools import lru_cache
from pathlib import Path

from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import timedelta


class JWT(BaseModel):
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

    @property
    def access_expire(self) -> timedelta:
        return timedelta(minutes=self.access_expire_minutes)

    @property
    def refresh_expire(self) -> timedelta:
        return timedelta(hours=self.refresh_expire_hours)


class Database(BaseModel):
    """Настройки базы данных"""
    host: str = Field(description="Хост базы данных")
    port: int = Field(description="Порт базы данных")
    db_name: str = Field(description="Имя базы данных")
    user: str = Field(description="Пользователь базы данных")
    password: str = Field(description="Пароль пользователя базы данных")

    @property
    def database_url(self) -> str:
        """
        :return: строка подключения к базе данных.
        """
        return (f"postgresql+asyncpg://{self.user}:{self.password}"
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
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    app_name: str = Field(
        default="Auth Service",
        description="Название сервиса"
    )
    env: str = Field(default="prod", description="Окружение выполнения")

    jwt: JWT = Field(description="Настройки JWT")
    bd: Database = Field(description="Настройки базы данных")
    cors: CORSSettings = Field(
        default_factory=CORSSettings,
        description="Настройки CORS"
    )


@lru_cache
def get_settings() -> Settings:
    """
    Кэшированный фабричный метод для получения настроек.
    Использует lru_cache для предотвращения повторного чтения .env файла.
    """
    return Settings()


# Глобальный экземпляр настроек для удобного импорта
settings = get_settings()