from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from libs.schemas.config import LogConfig, CORSSettings, RabbitMQConfig


class ServiceSettings(BaseModel):
    """Настройки сервиса"""
    protocol: str = Field(
        default="http",
        description="Протокол сервиса"
    )
    host: str = Field(
        default="127.0.0.1",
        description="Адрес сервиса"
    )
    port: int = Field(description="Порт сервиса")


class AuthCookieSettings(ServiceSettings):
    """Настройки кук авторизации"""
    access_token_cookie_name: str = Field(
        default="access_token",
        description="Имя куки для токена доступа"
    )
    refresh_token_cookie_name: str = Field(
        default="refresh_token",
        description="Имя куки для токена обновления"
    )
    cookie_secure: bool = Field(
        default=True,
        description="Флаг, указывающий на то, что куки должны быть защищены"
    )
    cookie_same_site: str = Field(
        default="lax",
        description="SameSite атрибут для кук"
    )


class SessionCookieSettings(BaseModel):
    """Настройки сессии"""
    name: str = Field(
        default="session_id",
        description="Имя куки сессии"
    )
    max_age: int = Field(
        default=3600,
        description="Максимальное время жизни куки сессии в секундах"
    )
    path: str = Field(
        default="/",
        description="Путь куки сессии"
    )


class JinjaTemplatesSettings(BaseModel):
    """Настройки шаблонизатора"""
    dir: str = Field(
        default="web_service/app/templates",
        description="Путь к директории с шаблонами"
    )
    static_dir: str = Field(
        default="web_service/app/static",
        description="Путь к директории со статикой"
    )
    static_url: str = Field(
        default="/static",
        description="URL префикс для статики"
    )


class JinjaSettings(BaseModel):
    """Настройки Jinja2"""
    templates: JinjaTemplatesSettings = Field(
        default_factory=JinjaTemplatesSettings,
        description="Настройки шаблонизатора"
    )
    auto_reload: bool = Field(
        default=False,
        description="Авто-перезагрузка шаблонов"
    )
    trim_blocks: bool = Field(
        default=True,
        description="Удалять пустые строки в шаблонах"
    )
    lstrip_blocks: bool = Field(
        default=True,
        description="Удалять пробелы слева от блоков"
    )


class PaginationSettings(BaseModel):
    default_limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Количество элементов на странице "
                    "по умолчанию"
    )
    max_limit: int = Field(
        default=100,
        ge=1,
        description="Максимальное количество элементов на странице"
    )


class Settings(BaseSettings):
    """Настройки приложения"""
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
        env_file=".env"
    )
    app_name: str = Field(
        default="Chat API service",
        description="Название сервиса"
    )
    env: str = Field(default="prod", description="Окружение выполнения")

    logs: LogConfig = Field(
        default_factory=LogConfig,
        description="Настройки логирования"
    )
    cors: CORSSettings = Field(
        default_factory=CORSSettings,
        description="Настройки CORS"
    )

    auth_service: ServiceSettings = Field(
        description="Настройки сервиса авторизации"
    )
    chat_api_service: ServiceSettings = Field(
        description="Настройки сервиса чата"
    )

    auth_cookie: AuthCookieSettings = Field(
        default_factory=AuthCookieSettings,
        description="Настройки кук авторизации"
    )

    session_cookie: SessionCookieSettings = Field(
        default_factory=SessionCookieSettings,
        description="Настройки сессии"
    )

    jinja: JinjaSettings = Field(
        default_factory=JinjaSettings,
        description="Настройки Jinja2"
    )

    pagination: PaginationSettings = Field(
        default_factory=PaginationSettings,
        description="Настройки пагинации"
    )

    rabbitmq: RabbitMQConfig = Field(
        description="Настройки RabbitMQ"
    )
