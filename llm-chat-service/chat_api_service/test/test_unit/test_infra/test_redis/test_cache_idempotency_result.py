import json
import pytest
from fakeredis.aioredis import FakeRedis
from uuid import uuid4

from chat_api_service.app.schemas.config import RedisConfig, RateLimitingConfig
from libs.schemas.llm_query import LLMTasksStatus
from libs.schemas.llm_query import LLMQueryResponse
from chat_api_service.app.infra.redis import RedisClient


@pytest.fixture
def sample_llm_response() -> LLMQueryResponse:
    """
    :return: Тестовый ответ LLMQueryResponse
    """
    return LLMQueryResponse(
        message_id=uuid4(),
        task_id="celery-task-abc-123",
        status=LLMTasksStatus.SUCCESS,
        conversation_id=uuid4(),
        content="Это тестовый ответ от LLM.",
        response_id=uuid4(),
        note="Сгенерировано для юнит-теста"
    )


@pytest.mark.asyncio
async def test_caches_response_successfully(
        fake_redis_client: FakeRedis,
        redis_config,
        sample_llm_response
):
    """
    Успешное кэширование валидного ответа.

    :param fake_redis_client: Мок клиента Redis.
    :param redis_config: Конфигурация Redis.
    :param sample_llm_response: Тестовый ответ LLM.
    """
    idem_key = "req_cached_success"

    await RedisClient.cache_idempotency_result(
        idem_key,
        sample_llm_response
    )

    cache_key = f"{redis_config.idem_key_prefix}:{idem_key}"
    assert await fake_redis_client.exists(cache_key) == 1

    stored_bytes = await fake_redis_client.get(cache_key)
    stored_dict = json.loads(stored_bytes)
    assert stored_dict == json.loads(sample_llm_response.model_dump_json())


@pytest.mark.asyncio
async def test_overwrites_existing_key_and_resets_ttl(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig
):
    """
    Повторное кэширование перезаписывает значение и сбрасывает TTL.

    :param fake_redis_client: Мок клиента Redis.
    :param redis_config: Конфигурация Redis.
    """
    idem_key = "req_overwrite"
    resp_v1 = LLMQueryResponse(
        message_id=uuid4(), task_id="v1", status=LLMTasksStatus.SUCCESS,
        conversation_id=uuid4(), content="Version 1"
    )
    resp_v2 = LLMQueryResponse(
        message_id=uuid4(), task_id="v2", status=LLMTasksStatus.SUCCESS,
        conversation_id=uuid4(), content="Version 2"
    )

    await RedisClient.cache_idempotency_result(idem_key, resp_v1)
    await RedisClient.cache_idempotency_result(idem_key, resp_v2)

    cache_key = f"{redis_config.idem_key_prefix}:{idem_key}"
    stored = json.loads(await fake_redis_client.get(cache_key))

    assert stored["content"] == "Version 2"
    assert stored["task_id"] == "v2"

    ttl = await fake_redis_client.ttl(cache_key)
    assert redis_config.cache_ttl - 2 <= ttl <= redis_config.cache_ttl


@pytest.mark.asyncio
async def test_write_and_read_consistency(
        fake_redis_client: FakeRedis,
        redis_config: RedisConfig,
        sample_llm_response: LLMQueryResponse
):
    """
    Записанный ответ корректно читается методом check_idempotency.

    :param fake_redis_client: Мок клиента Redis.
    :param redis_config: Конфигурация Redis.
    :param sample_llm_response: Тестовый ответ LLM.
    """
    idem_key = "roundtrip_key"

    await RedisClient.cache_idempotency_result(
        idem_key, sample_llm_response
    )
    cached = await RedisClient.check_idempotency(idem_key)
    assert cached is not None
    assert cached == json.loads(sample_llm_response.model_dump_json())
