import redis.asyncio as aioredis
from loguru import logger


class Redis:
    """Класс для управления асинхронным Redis-клиентом."""
    _redis_client: aioredis.Redis | None = None

    async def setup(self, redis_url: str):
        """Инициализация Redis клиента."""
        if self._redis_client is not None:
            raise SystemError("Redis клиент уже инициализирован.")
        self._redis_client = aioredis.from_url(redis_url)
        await self._redis_client.ping()
        logger.info("Redis клиент инициализирован.")

    async def close(self):
        """Закрытие Redis клиента."""
        if self._redis_client is not None:
            await self._redis_client.close()
            self._redis_client = None

    @property
    def client(self) -> aioredis.Redis:
        """
        :return: Redis клиент.
        """
        if self._redis_client is None:
            raise SystemError(
                "Redis клиент не инициализирован. "
                "Используйте setup() для инициализации."
            )
        return self._redis_client
