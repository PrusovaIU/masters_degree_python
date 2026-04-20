import asyncio

import pytest
from fakeredis.aioredis import FakeRedis

from chat_api_service.app.infra.redis import RedisClient
from chat_api_service.app.schemas.config import RedisConfig


@pytest.mark.asyncio
async def test_allows_request_under_limit(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    Запрос разрешён, когда количество запросов ниже лимита.

    :param fake_redis_client: Мок для Redis.
    :param redis_config: Конфигурация Redis.
    """
    user_id = "user_123"

    for i in range(3):
        result = await RedisClient.check_rate_limit(user_id)
        assert result is True, f"Запрос #{i + 1} должен быть разрешён"

    key = RedisClient.get_rate_limit_key(user_id)
    count = await fake_redis_client.zcard(key)
    assert count == 3

@pytest.mark.asyncio
async def test_blocks_request_at_limit(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    Запрос блокируется при достижении лимита.

    :param fake_redis_client: Мок для Redis.
    :param redis_config: Конфигурация Redis.
    """
    user_id = "user_456"

    for i in range(5):
        result = await RedisClient.check_rate_limit(user_id)
        assert result is True, f"Запрос #{i + 1} должен быть разрешён"

    result = await RedisClient.check_rate_limit(user_id)
    assert result is False, "6-й запрос должен быть заблокирован"

@pytest.mark.asyncio
async def test_sliding_window_removes_old_entries(
        fake_redis_client,
        redis_config
):
    """
    Старые записи за пределами окна удаляются, освобождая место.

    :fake_redis_client: Мок для Redis.
    :param redis_config: Конфигурация Redis.
    """
    user_id = "user_789"
    window = 2
    RedisClient._settings.rate_limit.llm_window = window

    # Заполняем лимит:
    for _ in range(5):
        await RedisClient.check_rate_limit(user_id)

    # Запрос вне лимита блокируется
    assert await RedisClient.check_rate_limit(user_id) is False
    await asyncio.sleep(window + 1)

    # За пределами окна:
    # Старые записи удалены, новый запрос должен пройти
    result = await RedisClient.check_rate_limit(user_id)
    assert result is True, \
        "Запрос после истечения окна должен быть разрешён"

    key = RedisClient.get_rate_limit_key(user_id)
    count = await fake_redis_client.zcard(key)
    assert count == 1

@pytest.mark.asyncio
async def test_ttl_set_on_rate_limit_key(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    На ключ rate limiting устанавливается корректный TTL.

    :param fake_redis_client: Мок для Redis.
    :param redis_config: Конфигурация Redis.
    """
    user_id = "user_ttl_test"
    window = redis_config.rate_limit.llm_window

    await RedisClient.check_rate_limit(user_id)

    key = RedisClient.get_rate_limit_key(user_id)
    ttl = await fake_redis_client.ttl(key)

    # TTL должен быть примерно равен window + 1 (из-за expire(key, window + 1))
    assert window <= ttl <= window + 2, \
        f"Ожидался TTL ~{window + 1}, получен {ttl}"

@pytest.mark.asyncio
async def test_different_users_have_separate_limits(
        fake_redis_client,
        redis_config
):
    """
    Разные пользователи имеют независимые лимиты.

    :param fake_redis_client: Мок для Redis.
    :param redis_config: Конфигурация Redis.
    """
    user_1 = "user_a"
    user_2 = "user_b"

    # Исчерпываем лимит для user_1
    for _ in range(5):
        await RedisClient.check_rate_limit(user_1)
    assert await RedisClient.check_rate_limit(user_1) is False

    # user_2 должен иметь свой независимый лимит
    result = await RedisClient.check_rate_limit(user_2)
    assert result is True, "Запрос другого пользователя должен быть разрешён"

    key_1 = RedisClient.get_rate_limit_key(user_1)
    key_2 = RedisClient.get_rate_limit_key(user_2)
    assert key_1 != key_2
