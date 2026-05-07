from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import fakeredis.aioredis
import pytest
from freezegun import freeze_time

from chat_api_service.app.infra.redis import RedisClient
from chat_api_service.app.schemas.config import RateLimitingConfig, RedisConfig


@pytest.fixture
def rate_limit_config() -> RateLimitingConfig:
    """
    Фикстура конфигурации rate limiting.
    :return: Тестовая конфигурация rate limiting.
    """
    return RateLimitingConfig(
        key="rate_limit:llm",
        llm_window=60,  # 60 секунд
        llm_limit=5,  # максимум 5 запросов
        lock_ttl=30
    )


@pytest.fixture
def redis_config(rate_limit_config) -> RedisConfig:
    """
    Фикстура основной конфигурации Redis.

    :param rate_limit_config: Конфигурация rate limiting.
    :return: Тестовая конфигурация Redis.
    """
    return RedisConfig(
        host="localhost",
        port=6379,
        db=0,
        password="",
        rate_limit=rate_limit_config,
        idem_key_prefix="idem:cache",
        cache_ttl=3600
    )


@pytest.fixture
async def fake_redis_client(redis_config) -> fakeredis.aioredis.FakeRedis:
    """
    Фикстура для инициализации RedisClient с fakeredis.

    :param redis_config: Конфигурация Redis.
    :return: Объект fakeredis.
    """
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=False)
    RedisClient._redis_client = fake_redis
    RedisClient._settings = redis_config
    yield fake_redis
    await fake_redis.aclose()
    RedisClient._redis_client = None
    RedisClient._settings = None


@pytest.fixture
def mock_datetime_helper():
    def _freeze(timestamp: float):
        return patch(
            "chat_api_service.app.infra.redis.datetime.now",
            return_value=datetime.fromtimestamp(timestamp, tz=timezone.utc)
        )

    return _freeze


@pytest.fixture
def mock_datetime_now(mock_datetime_helper):
    """Хелпер для мока datetime.now(timezone.utc)."""
    # with patch("chat_api_service.app.infra.redis.datetime.now") as mock:
    #     yield mock
    def _freeze(timestamp: float):
        return patch(
            "chat_api_service.app.infra.redis.datetime.now",
            return_value=datetime.fromtimestamp(timestamp, tz=timezone.utc)
        )

    return _freeze

