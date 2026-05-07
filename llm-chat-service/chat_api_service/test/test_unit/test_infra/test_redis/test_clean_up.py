from unittest.mock import AsyncMock, patch

import fakeredis.aioredis
import pytest
from fakeredis.aioredis import FakeRedis

from chat_api_service.app.infra.redis import RedisClient
from chat_api_service.app.schemas.config import RateLimitingConfig, RedisConfig


@pytest.mark.asyncio
async def test_clean_up_returns_zero_when_no_keys_exist(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    Если нет ключей блокировок, метод возвращает 0.

    :param fake_redis_client: Мок redis клиента.
    :param redis_config: Конфигурация Redis.
    """
    result = await RedisClient.clean_up()
    assert result == 0

@pytest.mark.asyncio
async def test_clean_up_deletes_keys_with_ttl_greater_than_config(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    Ключи с TTL > lock_ttl удаляются, метод возвращает их количество.

    :param fake_redis_client: Мок redis клиента.
    :param redis_config: Конфигурация Redis.
    """
    lock_ttl = redis_config.rate_limit.lock_ttl

    stale_keys = [
        RedisClient.get_redis_lock_key(f"stale_{i}")
        for i in range(3)
    ]
    for key in stale_keys:
        await fake_redis_client.set(key, "locked", ex=lock_ttl + 20)

    count = await RedisClient.clean_up()
    assert count == 3
    for key in stale_keys:
        assert await fake_redis_client.exists(key) == 0


@pytest.mark.asyncio
async def test_clean_up_preserves_keys_with_ttl_less_or_equal_to_config(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    Ключи с TTL <= lock_ttl не удаляются.

    :param fake_redis_client: Мок redis клиента.
    :param redis_config: Конфигурация Redis.
    """
    lock_ttl = redis_config.rate_limit.lock_ttl  # 30
    valid_keys = [
        RedisClient.get_redis_lock_key(f"valid_{i}")
        for i in range(2)
    ]

    for key in valid_keys:
        await fake_redis_client.set(key, "locked", ex=lock_ttl - 20)

    count = await RedisClient.clean_up()
    assert count == 0
    for key in valid_keys:
        assert await fake_redis_client.exists(key) == 1
        assert await fake_redis_client.ttl(key) > 0

@pytest.mark.asyncio
async def test_clean_up_boundary_exact_ttl(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    Ключ с TTL == lock_ttl НЕ удаляется (условие strict >).

    :param fake_redis_client: Мок redis клиента.
    :param redis_config: Конфигурация Redis.
    """
    lock_ttl = redis_config.rate_limit.lock_ttl
    key = RedisClient.get_redis_lock_key("exact_ttl")

    await fake_redis_client.set(key, "locked", ex=lock_ttl)

    count = await RedisClient.clean_up()
    assert count == 0
    assert await fake_redis_client.exists(key) == 1


@pytest.mark.asyncio
async def test_clean_up_ignores_keys_without_expiration(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    Ключи без TTL (TTL == -1) не удаляются.

    :param fake_redis_client: Мок redis клиента.
    :param redis_config: Конфигурация Redis.
    """
    key = RedisClient.get_redis_lock_key("persistent_lock")
    await fake_redis_client.set(key, "locked")

    count = await RedisClient.clean_up()
    assert count == 0
    assert await fake_redis_client.exists(key) == 1


@pytest.mark.asyncio
async def test_clean_up_does_not_delete_rate_limit_entries(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    clean_up не удаляет ключи rate limiting.

    :param fake_redis_client: Мок redis клиента.
    :param redis_config: Конфигурация Redis.
    """
    rl_key = RedisClient.get_rate_limit_key("user_rl")
    await fake_redis_client.zadd(rl_key, {"12345": 12345})
    await fake_redis_client.zadd(rl_key, {"67890": 67890})

    await RedisClient.clean_up()

    assert await fake_redis_client.zcard(rl_key) == 2


@pytest.mark.asyncio
async def test_clean_up_does_not_delete_idempotency_cache(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    clean_up не удаляет кэш идемпотентности.

    :param fake_redis_client: Мок redis клиента.
    :param redis_config: Конфигурация Redis.
    """
    cache_key = f"{redis_config.idem_key_prefix}:idem_test"
    await fake_redis_client.setex(
        cache_key,
        3600,
        b'{"status": "done"}'
    )

    await RedisClient.clean_up()
    cached = await fake_redis_client.get(cache_key)
    assert cached is not None
