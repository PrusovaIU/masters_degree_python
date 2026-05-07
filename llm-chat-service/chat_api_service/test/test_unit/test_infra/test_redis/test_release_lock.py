import pytest
from fakeredis.aioredis import FakeRedis

from chat_api_service.app.infra.redis import RedisClient
from chat_api_service.app.schemas.config import RedisConfig


@pytest.mark.asyncio
async def test_release_lock_success_existing_key(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    Блокировка успешно удаляется, если ключ существует.

    :param fake_redis_client: Мок клиента Redis.
    :param redis_config: Конфигурация Redis.
    """
    idempotency_key = "req_existing_lock"
    lock_key = RedisClient.get_redis_lock_key(idempotency_key)

    await fake_redis_client.set(lock_key, "locked", px=30000)
    assert await fake_redis_client.exists(lock_key) == 1

    result = await RedisClient.release_lock(idempotency_key)
    assert result is None

    assert await fake_redis_client.exists(lock_key) == 0


@pytest.mark.asyncio
async def test_release_lock_no_error_on_missing_key(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    Удаление несуществующего ключа не вызывает ошибку.
    """
    idempotency_key = "req_nonexistent"
    lock_key = RedisClient.get_redis_lock_key(idempotency_key)

    assert await fake_redis_client.exists(lock_key) == 0
    result = await RedisClient.release_lock(idempotency_key)

    assert result is None
    assert await fake_redis_client.exists(lock_key) == 0


@pytest.mark.asyncio
async def test_release_lock_after_acquire(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    release_lock корректно работает после acquire_lock.

    :param fake_redis_client: Мок клиента Redis.
    :param redis_config: Конфигурация Redis.
    """
    idempotency_key = "req_acquire_release"
    acquire_result = await RedisClient.acquire_lock(idempotency_key)
    assert acquire_result is True

    lock_key = RedisClient.get_redis_lock_key(idempotency_key)
    assert await fake_redis_client.exists(lock_key) == 1

    await RedisClient.release_lock(idempotency_key)
    assert await fake_redis_client.exists(lock_key) == 0

    re_acquire = await RedisClient.acquire_lock(idempotency_key)
    assert re_acquire is True


@pytest.mark.asyncio
async def test_release_lock_does_not_affect_other_keys(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    Удаление одной блокировки не затрагивает другие.

    :param fake_redis_client: Мок клиента Redis.
    :param redis_config: Конфигурация Redis.
    """
    key_1 = "req_first"
    key_2 = "req_second"
    key_3 = "req_third"

    for k in [key_1, key_2, key_3]:
        await fake_redis_client.set(
            RedisClient.get_redis_lock_key(k),
            "locked"
        )

    await RedisClient.release_lock(key_2)

    assert await fake_redis_client.exists(
        RedisClient.get_redis_lock_key(key_1)
    ) == 1, "key_1 должен остаться"
    assert await fake_redis_client.exists(
        RedisClient.get_redis_lock_key(key_2)
    ) == 0, "key_2 должен быть удалён"
    assert await fake_redis_client.exists(
        RedisClient.get_redis_lock_key(key_3)
    ) == 1, "key_3 должен остаться"


@pytest.mark.asyncio
async def test_release_lock_with_empty_string_key(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    Поведение при пустом idempotency_key.

    :param fake_redis_client: Мок клиента Redis.
    :param redis_config: Конфигурация Redis.
    """
    idempotency_key = ""
    lock_key = RedisClient.get_redis_lock_key(idempotency_key)

    await fake_redis_client.set(lock_key, "locked")
    await RedisClient.release_lock(idempotency_key)

    assert await fake_redis_client.exists(lock_key) == 0


@pytest.mark.asyncio
async def test_release_lock_does_not_clear_rate_limit_keys(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    release_lock не удаляет ключи rate limiting.

    :param fake_redis_client: Мок клиента Redis.
    :param redis_config: Конфигурация Redis.
    """
    user_id = "user_rl_test"
    rl_key = RedisClient.get_rate_limit_key(user_id)

    await fake_redis_client.zadd(rl_key, {"123456": 123456})
    assert await fake_redis_client.zcard(rl_key) == 1

    await RedisClient.release_lock("some_lock_key")
    assert await fake_redis_client.zcard(rl_key) == 1


@pytest.mark.asyncio
async def test_release_lock_does_not_affect_idempotency_cache(
        fake_redis_client, redis_config
):
    """
    release_lock не удаляет кэш идемпотентности.

    :param fake_redis_client: Мок клиента Redis.
    :param redis_config: Конфигурация Redis.
    """
    idempotency_key = "idem_cache_test"
    cache_key = f"{redis_config.idem_key_prefix}:{idempotency_key}"

    await fake_redis_client.setex(
        cache_key,
        3600,
        b'{"result": "cached_value"}'
    )

    lock_key = RedisClient.get_redis_lock_key(idempotency_key)
    await fake_redis_client.set(lock_key, "locked")
    await RedisClient.release_lock(idempotency_key)

    cached = await fake_redis_client.get(cache_key)
    assert cached is not None
