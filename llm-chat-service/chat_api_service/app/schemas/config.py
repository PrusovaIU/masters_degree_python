from pydantic import Field, computed_field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from libs.schemas.config import LogConfig, DatabaseConfig, JWTSecret, CORSSettings
from urllib.parse import quote_plus


class ConfigWithPasswd(BaseModel):
    password: str = Field(description="Пароль")

    @computed_field
    @property
    def password_quoted(self) -> str:
        """
        :return: Пароль с экранированными символами.
        """
        return f":{quote_plus(self.password)}@" \
            if self.password \
            else ""


class RateLimitingConfig(BaseModel):
    """
    Конфигурация Rate Limiting
    """
    key: str = Field(
        default="rl:llm:requests",
        description="Ключ для Rate Limiting"
    )
    llm_window: int = Field(
        default=60,
        description="Время окна в секундах"
    )
    llm_limit: int = Field(
        default=10,
        description="Количество запросов в минуту"
    )
    lock_ttl: int = Field(
        default=300,
        description="Время блокировки от дубликатов запросов в секундах"
    )


class RedisConfig(ConfigWithPasswd):
    """Конфигурация Redis"""
    host: str = Field(description="Хост Redis сервера")
    port: int = Field(description="Порт Redis сервера")
    user: str = Field(description="Имя пользователя Redis")
    db: int = Field(default="0", description="Номер базы данных Redis")
    timeout: int = Field(
        default=30,
        description="Таймаут соединения в секундах"
    )
    rate_limit: RateLimitingConfig = Field(
        default_factory=RateLimitingConfig,
        description="Настройки Rate Limiting"
    )
    idem_key_prefix: str = Field(
        default="idem:cache",
        description="Префикс ключа для идемпотентности"
    )
    cache_ttl: int = Field(
        default=3600,
        description="Время жизни кэша в секундах"
    )

    @computed_field
    @property
    def url(self) -> str:
        """
        :return: Строка подключения к Redis.
        """
        return (f"redis://{self.password_quoted}{self.host}:"
                f"{self.port}/{self.db}")


class RabbitMQConfig(ConfigWithPasswd):
    """Конфигурация RabbitMQ"""
    host: str = Field(description="Хост RabbitMQ сервера")
    port: int = Field(description="Порт RabbitMQ сервера")
    user: str = Field(description="Имя пользователя RabbitMQ")
    vhost: str = Field(description="Виртуальный хост RabbitMQ")


class JWTConfig(BaseModel):
    """Конфигурация JWT"""
    secret: JWTSecret = Field(description="Секретный ключ JWT")
    alg: str = Field(default="HS256", description="Алгоритм шифрования JWT")
    header_name: str = Field(
        default="Authorization",
        description="Имя заголовка для JWT"
    )


class OpenRouterConfig(BaseModel):
    """
    Схема настроек OpenRouter
    """
    api_key: str = Field(
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
    app_name: str = Field(
        default="llm-fastapi-openrouter",
        description="Заголовок приложения для OpenRouter"
    )
    referer: str = Field(
        description="Реферер для OpenRouter"
    )
    title: str = Field(
        default="llm-fastapi-openrouter",
        description="Заголовок запроса"
    )
    request_timeout: int = Field(
        default=10,
        description="Таймаут запроса в секундах"
    )


class Settings(BaseSettings):
    """Настройки приложения"""
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
    cors: CORSSettings = Field(
        default_factory=CORSSettings,
        description="Настройки CORS"
    )

    db: DatabaseConfig = Field(description="Настройки базы данных")
    redis: RedisConfig = Field(description="Настройки Redis")
    rabbitmq: RabbitMQConfig = Field(description="Настройки RabbitMQ")
    openrouter: OpenRouterConfig = Field(
        description="Настройки подключения к OpenRouter"
    )

    jwt: JWTConfig = Field(description="Настройки JWT")

    @computed_field
    @property
    def celery_broker_url(self) -> str:
        """
        :return: Строка подключения к RabbitMQ для Celery Broker.
        """
        return (
            f"amqp://{self.rabbitmq.user}:"
            f"{self.rabbitmq.password_quoted}@"
            f"{self.rabbitmq.host}:{self.rabbitmq.port}/{self.rabbitmq.vhost}"
        )

    @computed_field
    @property
    def celery_result_backend(self) -> str:
        """
        :return: Строка подключения к Redis для Celery Result Backend.
        """
        return (f"redis://{self.redis.password_quoted}{self.redis.host}:"
                f"{self.redis.port}/{self.redis.db + 1}")
