import hashlib
import time
from uuid import UUID
from chat_api_service.app.infra.redis import RedisClient
from chat_api_service.app.schemas.llm import LLMQueryResponse


def generate_idempotency_key(
        user_id: str,
        conversation_id: UUID,
        content: str,
        timestamp: float | None = None
) -> str:
    """
    Генерация уникального ключа идемпотентности для запроса.

    Ключ формируется на основе:
    - user_id
    - conversation_id
    - content (хэш)
    - model (опционально)
    - временной метки (окно 60 секунд)

    :param user_id: ID пользователя.

    :param conversation_id: UUID диалога.

    :param content: Текст сообщения.

    :param timestamp: Временная метка для группировки
        (по умолчанию округляется до минуты).

    :return: Уникальный ключ идемпотентности.
    """
    ts = timestamp or time.time()
    window_ts = int(ts // 60) * 60
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    key_parts = [
        user_id,
        str(conversation_id),
        content_hash,
        str(window_ts),
    ]
    raw_key = ":".join(key_parts)
    return f"idem:{hashlib.sha256(raw_key.encode()).hexdigest()}"


async def check_idempotency_cache(
        user_id: str,
        conversation_id: UUID,
        content: str,
        custom_idem_key: str | None
) -> LLMQueryResponse | None:
    """
    Проверка кэша идемпотентности. Если ключ найден, возвращается ответ из
    кэша.

    :param user_id: Идентификатор пользователя.
    :param conversation_id: ID диалога.
    :param content: Контент сообщения.
    :param custom_idem_key: Пользовательский ключ идемпотентности.
    :return: Закэшированный ответ или None.
    """
    if custom_idem_key:
        idempotency_key = custom_idem_key
    else:
        idempotency_key = generate_idempotency_key(
            user_id=user_id,
            conversation_id=conversation_id,
            content=content
        )
    cache: dict | None = await RedisClient.check_idempotency(idempotency_key)
    return LLMQueryResponse(**cache) if cache else None
