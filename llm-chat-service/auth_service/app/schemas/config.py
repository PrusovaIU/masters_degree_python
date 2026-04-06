from datetime import timedelta

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from libs.schemas.config import JWTSecret, DatabaseConfig, CORSSettings, \
    LogConfig


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


class PasswordHashConfig(BaseModel):
    schemes: list[str] = Field(
        default=["bcrypt"],
        description="Список используемых схем хеширования паролей"
    )
    bcrypt_rounds: int = Field(
        default=12,
        description="Количество раундов для хеширования паролей"
    )


class Settings(BaseSettings):
    """
    Настройки приложения, загружаемые из переменных окружения.
    """

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__"
    )
    app_name: str = Field(
        default="Auth Service",
        description="Название сервиса"
    )
    env: str = Field(default="prod", description="Окружение выполнения")
    logs: LogConfig = Field(
        default_factory=LogConfig,
        description="Настройки логирования"
    )

    jwt: JWTConfig = Field(description="Настройки JWT")
    db: DatabaseConfig = Field(description="Настройки базы данных")
    password_hash: PasswordHashConfig = Field(
        description="Настройки хеширования паролей",
        default_factory=PasswordHashConfig
    )
    cors: CORSSettings = Field(
        default_factory=CORSSettings,
        description="Настройки CORS"
    )
