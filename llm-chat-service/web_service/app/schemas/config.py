from typing import Self

from pydantic import Field, BaseModel, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from libs.schemas.config import LogConfig, CORSSettings, RabbitMQConfig
from fastapi.templating import Jinja2Templates


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
    timeout: int = Field(
        default=10,
        description="Таймаут запроса"
    )

    @property
    def url(self) -> str:
        """
        :return: URL сервиса.
        """
        return f"{self.protocol}://{self.host}:{self.port}"


class AuthCookieSettings(BaseModel):
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


class CookieSettings(BaseModel):
    user_id_cookie_name: str = Field(
        default="user_id",
        description="Имя куки для ID пользователя"
    )
    user_email_cookie_name: str = Field(
        default="user_email",
        description="Имя куки для email пользователя"
    )
    user_role_cookie_name: str = Field(
        default="user_role",
        description="Имя куки для роли пользователя"
    )


class JinjaSettings(BaseModel):
    """Настройки шаблонизатора"""
    dir: str = Field(
        default="./web_service/app/templates",
        description="Путь к директории с шаблонами"
    )

    _templates: Jinja2Templates | None = None

    @model_validator(mode="after")
    def init_templates(self) -> Self:
        self._templates = Jinja2Templates(
            directory=self.dir
        )
        return self

    @property
    def templates(self) -> Jinja2Templates:
        return self._templates


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

    cookie: CookieSettings = Field(
        default_factory=CookieSettings,
        description="Настройки кук"
    )

    jinja: JinjaSettings = Field(
        default_factory=JinjaSettings,
        description="Настройки Jinja2"
    )

    rabbitmq: RabbitMQConfig = Field(
        description="Настройки RabbitMQ"
    )

    auth_header_name: str = Field(
        default="Authorization",
        description="Имя заголовка с токеном авторизации"
    )

    _cookies: tuple[str, ...] | None = None

    @model_validator(mode="after")
    def set_cookies(self) -> Self:
        self._cookies = (
            self.auth_cookie.access_token_cookie_name,
            self.auth_cookie.refresh_token_cookie_name,
            self.cookie.user_id_cookie_name,
            self.cookie.user_email_cookie_name,
            self.cookie.user_role_cookie_name
        )
        return self

    @property
    def cookies(self) -> tuple[str, ...]:
        """
        :return: Список имен кук.
        """
        return self._cookies
