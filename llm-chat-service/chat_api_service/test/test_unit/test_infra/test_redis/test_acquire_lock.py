import pytest
from fakeredis.aioredis import FakeRedis

from chat_api_service.app.infra.redis import RedisClient
from chat_api_service.app.schemas.config import RedisConfig


@pytest.mark.asyncio
async def test_acquire_lock_success_when_key_not_exists(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    Блокировка успешно получена, если ключа не существует.

    :param fake_redis_client: Мок Redis клиента.
    :param redis_config: Конфигурация Redis.
    """
    idempotency_key = "req_abc123"

    result = await RedisClient.acquire_lock(idempotency_key)

    assert result is True, "Блокировка должна быть получена"

    lock_key = RedisClient.get_redis_lock_key(idempotency_key)
    value = await fake_redis_client.get(lock_key)
    assert value == b"locked", "Значение блокировки должно быть 'locked'"


@pytest.mark.asyncio
async def test_acquire_lock_fails_when_key_already_exists(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    Блокировка не получена, если ключ уже занят.

    :param fake_redis_client: Мок Redis клиента.
    :param redis_config: Конфигурация Redis.
    """
    idempotency_key = "req_xyz789"
    lock_key = RedisClient.get_redis_lock_key(idempotency_key)

    await fake_redis_client.set(lock_key, "locked", nx=True, px=30000)

    result = await RedisClient.acquire_lock(idempotency_key)
    assert result is False, "Блокировка не должна быть получена повторно"


@pytest.mark.asyncio
async def test_acquire_lock_with_custom_ttl(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    Пользовательский TTL переопределяет значение из конфигурации.

    :param fake_redis_client: Мок Redis клиента.
    :param redis_config: Конфигурация Redis.
    """
    idempotency_key = "req_custom_ttl"
    custom_ttl = 120

    await RedisClient.acquire_lock(idempotency_key, ttl=custom_ttl)

    lock_key = RedisClient.get_redis_lock_key(idempotency_key)
    ttl = await fake_redis_client.ttl(lock_key)

    assert custom_ttl - 2 <= ttl <= custom_ttl, \
        f"Ожидался TTL ~{custom_ttl}, получен {ttl}"
