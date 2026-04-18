import hashlib
import time
from uuid import UUID


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
