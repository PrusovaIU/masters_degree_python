from datetime import datetime, timezone

import redis.asyncio as aioredis
from loguru import logger
from chat_api_service.app.schemas.config import RedisConfig


class RedisClient:
    """Класс для управления асинхронным Redis-клиентом."""
    _redis_client: aioredis.Redis | None = None
    _settings: RedisConfig | None = None

    async def setup(self, settings: RedisConfig):
        """Инициализация Redis клиента."""
        if self._redis_client is not None:
            raise SystemError("Redis клиент уже инициализирован.")
        self._settings = settings
        self._redis_client = aioredis.from_url(settings.url)
        await self._redis_client.ping()
        logger.info("Redis клиент инициализирован.")

    async def close(self):
        """Закрытие Redis клиента."""
        if self._redis_client is not None:
            await self._redis_client.close()
            self._redis_client = None

    @classmethod
    def client(cls) -> aioredis.Redis:
        """
        :return: Redis клиент.
        """
        if cls._redis_client is None:
            raise SystemError(
                "Redis клиент не инициализирован. "
                "Используйте setup() для инициализации."
            )
        return cls._redis_client

    @classmethod
    def get_rate_limit_key(cls, user_id: str) -> str:
        """
        Формирование ключа для rate limiting.

        :param user_id: ID пользователя.
        :return: Ключ для Redis.
        """
        return f"{cls._settings.rate_limit.key}:{user_id}"

    @staticmethod
    def get_redis_lock_key(idempotency_key: str) -> str:
        """
        Формирование ключа блокировки для предотвращения дубликатов.

        :param idempotency_key: Уникальный ключ запроса.
        :return: Ключ для Redis.
        """
        return f"llm:lock:{idempotency_key}"

    @classmethod
    async def check_rate_limit(cls, user_id: str) -> bool:
        """
        Проверка лимита запросов к LLM(sliding window).

        :param user_id: ID пользователя.
        :return: True если запрос разрешён, False если лимит превышен.
        """
        redis = cls._redis_client
        key: str = cls.get_rate_limit_key(user_id)
        window: int = cls._settings.rate_limit.llm_window
        limit: int = cls._settings.rate_limit.llm_limit

        now = datetime.now(timezone.utc).timestamp()
        window_start = now - window

        # Удаление старых записей за пределами окна
        await redis.zremrangebyscore(key, 0, window_start)

        # Подсчет текущего количества запросов
        current_count = await redis.zcard(key)

        if current_count >= limit:
            return False

        # Добавление нового запроса в окно
        await redis.zadd(key, {f"{now}": now})
        # Установка TTL для автоочистки ключа
        await redis.expire(key, window + 1)

        return True

    @classmethod
    async def acquire_lock(cls, idempotency_key: str, ttl: int = None) -> bool:
        """
        Попытка получения блокировки в Redis.

        :param idempotency_key: Уникальный ключ запроса.
        :param ttl: Время жизни блокировки в секундах.
        :return: True если блокировка получена, False если уже занята.
        """
        redis = cls._redis_client
        lock_key = cls.get_redis_lock_key(idempotency_key)
        lock_ttl = ttl or cls._settings.rate_limit.lock_ttl

        result = await redis.set(
            lock_key,
            "locked",
            nx=True,
            px=lock_ttl * 1000
        )
        return bool(result)

    @classmethod
    async def _release_lock(cls, idempotency_key: str) -> None:
        """
        Освобождение блокировки.

        :param idempotency_key: Уникальный ключ запроса.
        """
        redis = cls._redis_client
        lock_key = cls.get_redis_lock_key(idempotency_key)
        await redis.delete(lock_key)
