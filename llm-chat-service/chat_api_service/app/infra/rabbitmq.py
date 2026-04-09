from collections.abc import Callable, Awaitable
from datetime import datetime
from typing import Any

from aio_pika import Message, connect_robust, IncomingMessage
from aio_pika.abc import DeliveryMode, AbstractRobustConnection, \
    AbstractRobustChannel, AbstractRobustQueue, AbstractRobustExchange
import asyncio
from loguru import logger
from chat_api_service.app.core.exceptions import rabbitmq as errors
from chat_api_service.app.core.rabbitmq_utils import RabbitMQConsumeUtils


class RabbitMQClient:

    _connection: AbstractRobustConnection | None = None
    _channel: AbstractRobustChannel | None = None
    _is_connected: bool = False
    _lock: asyncio.Lock = asyncio.Lock()
    _reconnect_task: asyncio.Task | None = None
    _on_reconnect_callbacks: list[Callable[[], Awaitable[None]]] = []

    def __init__(
            self,
            url: str,
            reconnect_interval: int = 5,
            max_reconnect_attempts: int = 10,
            timeout: int = 5,
    ):
        """
        Инициализация клиента.

        :param url: URL подключения к RabbitMQ (amqp://...).

        :param reconnect_interval: Интервал между попытками
            переподключения (сек).

        :param max_reconnect_attempts: Максимальное количество попыток
            переподключения.
        """
        self._url = url
        self._timeout = timeout
        self._reconnect_interval = reconnect_interval
        self._max_reconnect_attempts = max_reconnect_attempts
        self._connection_params = {
            "url": self._url,
            "timeout": timeout
        }

    @classmethod
    async def setup(
            cls,
            url: str | None = None,
            timeout: int = 5,
            has_set: bool = False,
    ) -> None:
        """
        Инициализация глобального экземпляра клиента.

        :param url: URL подключения к RabbitMQ.
        :param timeout: Таймаут подключения.
        :param has_set: Разрешить перезапись существующего подключения.
        :return: None.

        :raises SystemError: Если клиент уже инициализирован.
        """
        if cls._connection is not None and not has_set:
            raise SystemError("RabbitMQ клиент уже инициализирован.")

        cls._connection = await connect_robust(
            url=url,
            timeout=timeout,
            loop=asyncio.get_event_loop(),
        )
        cls._channel = await cls._connection.channel()
        await cls._channel.set_qos(prefetch_count=10)
        cls._is_connected = True
        logger.info("RabbitMQ клиент инициализирован.")

    @classmethod
    async def close(cls) -> None:
        """Закрытие глобального подключения."""
        if cls._connection and not cls._connection.is_closed:
            await cls._connection.close()
            cls._connection = None
            cls._channel = None
            cls._is_connected = False
            logger.info("RabbitMQ подключение закрыто.")

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @classmethod
    async def publish(
            cls,
            body: bytes,
            exchange_name: str,
            routing_key: str = "",
            persistent: bool = True,
            priority: int | None = None,
            expiration: int | None = None,
            message_id: str | None = None,
            headers: dict[str, Any] | None = None,
    ) -> None:
        """
        Отправка сообщения в очередь.

        :param body: Тело сообщения.
        :param exchange_name: Имя exchange.
        :param routing_key: Ключ маршрутизации.
        :param persistent: Если True, сообщение будет сохранено на диск.
        :param priority: Приоритет сообщения.
        :param expiration: TTL сообщения в миллисекундах.
        :param message_id: Идентификатор сообщения.
        :param headers: Дополнительные заголовки сообщения.
        :return: None.

        :raises RabbitMQPublishError: Если сообщение не отправлено.
        """
        if priority is not None and not (0 <= priority <= 9):
            raise ValueError(
                "Значение параметра priority должно быть от 0 до 9."
            )
        delivery_mode = DeliveryMode.PERSISTENT if persistent \
            else DeliveryMode.TRANSIENT
        message = Message(
            body=body,
            content_type="application/json",
            delivery_mode=delivery_mode,
            priority=priority,
            expiration=str(expiration) if expiration else None,
            message_id=message_id,
            headers=headers or {},
            timestamp=datetime.now()
        )
        try:
            exchange: AbstractRobustExchange = \
                await cls._channel.declare_exchange(
                    name=exchange_name,
                    durable=True
                )
            await exchange.publish(message, routing_key=routing_key)
            logger.debug(
                f"Сообщение успешно отправлено в RabbitMQ.",
                exchange=exchange_name,
                routing_key=routing_key,
                message_id=message_id
            )
        except Exception as err:
            logger.error(
                f"Ошибка публикации сообщения в RabbitMQ: "
                f"{err} ({err.__class__.__name__})",
                exchange=exchange_name,
                routing_key=routing_key,
                message_id=message_id,
            )
            raise errors.RabbitMQPublishError(
                str(err),
                exchange_name,
                routing_key
            )

    async def consume(
            self,
            queue_name: str,
            callback: Callable[[IncomingMessage], Awaitable[None]],
            auto_ack: bool = False,
            exclusive: bool = False,
    ) -> AbstractRobustQueue:
        """
        Начало обработки сообщений из очереди.

        :param queue_name: Имя очереди.

        :param callback: Асинхронный обработчик сообщений.

        :param auto_ack: Если True, сообщения будут подтверждаться
            автоматически.

        :param exclusive: Эксклюзивное потребление.

        :return: Объект очереди с активным consumer.
        """
        queue: AbstractRobustQueue = await self._channel.declare_queue(
            name=queue_name,
            durable=True,
            auto_delete=False
        )
        wrapped_callback = RabbitMQConsumeUtils(
            queue_name,
            callback,
            auto_ack
        ).wrapped_callback
        await queue.consume(wrapped_callback, exclusive=exclusive)
        logger.info(f"Старт обработки сообщений из очереди {queue_name}.")
        return queue
