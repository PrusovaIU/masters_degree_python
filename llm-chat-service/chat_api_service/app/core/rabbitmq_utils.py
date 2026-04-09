from collections.abc import Callable, Awaitable

from aio_pika import IncomingMessage
from loguru import logger


class RabbitMQConsumeUtils:
    """
    Утилиты для работы с очередью RabbitMQ.
    """
    def __init__(
            self,
            queue_name: str,
            callback: Callable[[IncomingMessage], Awaitable[None]],
            auto_ack: bool = False
    ):
        """
        :param queue_name: Имя очереди.
        :param callback: Асинхронный обработчик сообщений.
        :param auto_ack: Автоматически подтверждать получение.
        """
        self._queue_name = queue_name
        self._callback = callback
        self._auto_ack = auto_ack

    async def wrapped_callback(self, message: IncomingMessage):
        async with message.process(requeue=not self._auto_ack):
            try:
                await self._callback(message)
            except Exception as err:
                logger.error(
                    f"Error processing message: {err}",
                    message_id=message.message_id,
                    queue=self._queue_name,
                )
                if not self._auto_ack:
                    raise
