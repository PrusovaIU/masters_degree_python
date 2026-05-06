from aio_pika import connect_robust, Channel, Connection
import json
import asyncio

from aio_pika.abc import AbstractIncomingMessage
from loguru import logger
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator


class RabbitMQClient:
    """Клиент для работы с RabbitMQ"""

    def __init__(self, url: str):
        self._url = url
        self._connection: Connection | None = None
        self._channel: Channel | None = None

    async def connect(self) -> None:
        """Подключение к RabbitMQ."""
        try:
            self._connection = await connect_robust(self._url)
            self._channel = await self._connection.channel()
            logger.success(f"Подключено к RabbitMQ: {self._url}")
        except Exception as err:
            logger.error(
                f"Не удалось подключиться к RabbitMQ: "
                f"{err} ({err.__class__.__name__})"
            )
            raise

    async def close(self) -> None:
        """Закрытие подключения к RabbitMQ"""
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            print("RabbitMQ connection closed")

    def is_connected(self) -> bool:
        """
        Проверка подключения к RabbitMQ.

        :return: True, если подключено, иначе False.
        """
        if not self._channel:
            return False
        return True

    @property
    def channel(self) -> Channel | None:
        """Получение канала подключения."""
        return self._channel

    @asynccontextmanager
    async def consume_messages(
            self,
            queue_name: str
    ) -> AsyncGenerator[str]:
        """
        Старт цикла обработки сообщений из очереди.

        :param queue_name: Имя очереди.

        :yield: Сообщение пользователю.
        """
        logger.info(f"Начало обработки сообщений из очереди {queue_name}")
        queue = await self._channel.declare_queue(
            queue_name,
            durable=True
        )
        try:
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with self._handle_message(message) as data:
                        yield data
        except asyncio.CancelledError:
            logger.error(
                f"SSE stream завершен для очереди {queue_name}"
            )
        except Exception as err:
            logger.error(
                f"Ошибка SSE stream: "
                f"{err} ({err.__class__.__name__})"
            )
            data = json.dumps({"error": str(err)})
            yield f"data: {data}\n\n"
        finally:
            logger.info(
                f"Завершение обработки сообщений из очереди {queue_name}"
            )

    @staticmethod
    @asynccontextmanager
    async def _handle_message(
            message: AbstractIncomingMessage
    ) -> AsyncGenerator[str]:
        try:
            body = message.body.decode()
            data = json.loads(body)
            yield f"data: {json.dumps(data)}\n\n"
            await message.ack()
        except Exception as err:
            logger.error(
                f"Ошибка обработки сообщения: "
                f"{err} ({err.__class__.__name__})"
            )
            await message.nack(requeue=False)
