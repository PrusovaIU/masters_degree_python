import asyncio
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from fakeredis.aioredis import FakeRedis
from freezegun import freeze_time

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
    """Старые записи за пределами окна удаляются, освобождая место."""
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

