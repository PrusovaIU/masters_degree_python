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

#     @pytest.mark.asyncio
#     async def test_different_users_have_separate_limits(self,
#                                                         fake_redis_client,
#                                                         redis_config):
#         """Разные пользователи имеют независимые лимиты."""
#         user_1 = "user_a"
#         user_2 = "user_b"
#
#         # Исчерпываем лимит для user_1
#         for _ in range(5):
#             await RedisClient.check_rate_limit(user_1)
#         assert await RedisClient.check_rate_limit(user_1) is False
#
#         # user_2 должен иметь свой независимый лимит
#         result = await RedisClient.check_rate_limit(user_2)
#         assert result is True, "Запрос другого пользователя должен быть разрешён"
#
#         # Проверяем, что ключи разные
#         key_1 = RedisClient.get_rate_limit_key(user_1)
#         key_2 = RedisClient.get_rate_limit_key(user_2)
#         assert key_1 != key_2
#
#     @pytest.mark.asyncio
#     async def test_boundary_condition_exact_window(
#             self, fake_redis_client, redis_config
#     ):
#         """Записи на границе окна: ровно window секунд назад ещё учитываются."""
#         user_id = "user_boundary"
#         window = redis_config.rate_limit.llm_window
#         base_time = 2000000.0
#
#         # Добавляем запись ровно window секунд назад
#         with patch(
#                 "chat_api_service.app.infra.redis.datetime.now",
#                 return_value=datetime.fromtimestamp(base_time, tz=timezone.utc)
#         ):
#             await RedisClient.check_rate_limit(user_id)
#
#         # Проверяем в момент base_time + window (запись ещё в окне)
#         with patch(
#                 "chat_api_service.app.infra.redis.datetime.now",
#                 return_value=datetime.fromtimestamp(base_time + window,
#                                                     tz=timezone.utc)
#         ):
#             # Запись на границе ещё не удалена (zremrangebyscore удаляет < window_start)
#             # Поэтому при лимите=5 у нас уже 1 запись, можно сделать ещё 4
#             for i in range(4):
#                 result = await RedisClient.check_rate_limit(user_id)
#                 assert result is True
#
#             # 5-й дополнительный запрос (итого 5 в окне) — последний разрешённый
#             result = await RedisClient.check_rate_limit(user_id)
#             assert result is True
#
#             # 6-й — блокировка
#             assert await RedisClient.check_rate_limit(user_id) is False
#
#     @pytest.mark.asyncio
#     async def test_score_format_in_zadd(self, fake_redis_client, redis_config):
#         """Проверяем, что в zadd добавляется корректный формат {timestamp: score}."""
#         user_id = "user_score_test"
#         test_time = 1234567.89
#
#         with patch(
#                 "chat_api_service.app.infra.redis.datetime.now",
#                 return_value=datetime.fromtimestamp(test_time, tz=timezone.utc)
#         ):
#             await RedisClient.check_rate_limit(user_id)
#
#         key = RedisClient.get_rate_limit_key(user_id)
#         # Получаем все элементы с их скорингом
#         entries = await fake_redis_client.zrange(key, 0, -1, withscores=True)
#
#         assert len(entries) == 1
#         member, score = entries[0]
#         # member — это строка вида "1234567.89", score — число
#         assert float(member.decode() if isinstance(member,
#                                                    bytes) else member) == test_time
#         assert score == test_time
#
#
# # ========================
# # Дополнительные тесты для edge-cases
# # ========================
#
# @pytest.mark.asyncio
# async def test_check_rate_limit_with_zero_limit_config(
#         fake_redis_client, redis_config
# ):
#     """Поведение при лимите = 0: все запросы блокируются."""
#     redis_config.rate_limit.llm_limit = 0
#     user_id = "user_zero_limit"
#
#     result = await RedisClient.check_rate_limit(user_id)
#     assert result is False, "При лимите 0 все запросы должны блокироваться"
#
#
# @pytest.mark.asyncio
# async def test_check_rate_limit_idempotent_within_same_timestamp(
#         fake_redis_client, redis_config
# ):
#     """Несколько вызовов в одну и ту же миллисекунду корректно учитываются."""
#     user_id = "user_idem_test"
#     fixed_time = 999999.123
#
#     with patch(
#             "chat_api_service.app.infra.redis.datetime.now",
#             return_value=datetime.fromtimestamp(fixed_time, tz=timezone.utc)
#     ):
#         # Даже при одинаковом timestamp каждый вызов — отдельный запрос
#         results = [
#             await RedisClient.check_rate_limit(user_id)
#             for _ in range(7)  # 7 > лимита 5
#         ]
#
#         # Первые 5 — True, последние 2 — False
#         assert results[:5] == [True] * 5
#         assert results[5:] == [False] * 2