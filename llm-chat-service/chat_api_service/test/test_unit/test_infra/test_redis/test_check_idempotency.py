import json
import pytest
from fakeredis.aioredis import FakeRedis
from unittest.mock import patch

from chat_api_service.app.schemas.config import RedisConfig, RateLimitingConfig
from chat_api_service.app.infra.redis import RedisClient


@pytest.mark.asyncio
async def test_returns_parsed_dict_when_cache_exists(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    Возвращает кэш, если ключ присутствует в Redis.

    :param fake_redis_client: Мок Redis клиента.
    :param redis_config: Конфиг Redis.
    """
    idempotency_key = "req_cached_001"
    cache_key = f"{redis_config.idem_key_prefix}:{idempotency_key}"

    original_data = {
        "test": "test_returns_parsed_dict_when_cache_exists"
    }
    await fake_redis_client.set(cache_key, json.dumps(original_data))

    result = await RedisClient.check_idempotency(idempotency_key)
    assert result == original_data
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_returns_none_when_cache_miss(
        fake_redis_client: FakeRedis
):
    """
    Возвращает None, если ключ отсутствует в кэше.

    :param fake_redis_client: Мок Redis клиента.
    """
    result = await RedisClient.check_idempotency("req_nonexistent")
    assert result is None
