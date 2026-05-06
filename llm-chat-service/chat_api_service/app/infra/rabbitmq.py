from datetime import datetime
from typing import Any
from uuid import UUID

from aio_pika import Message, connect_robust
from aio_pika.abc import DeliveryMode, AbstractRobustConnection, \
    AbstractRobustChannel
import asyncio
from loguru import logger
from chat_api_service.app.core.exceptions import rabbitmq as errors


class RabbitMQClient:

    _connection: AbstractRobustConnection | None = None
    _channel: AbstractRobustChannel | None = None
    _is_connected: bool = False
    _queue_name: str | None = None

    @classmethod
    async def setup(
            cls,
            url: str,
            queue_name: str,
            timeout: int = 5,
            has_set: bool = False,
    ) -> None:
        """
        Инициализация глобального экземпляра клиента.

        :param url: URL подключения к RabbitMQ.
        :param queue_name: Имя очереди.
        :param timeout: Таймаут подключения.
        :param has_set: Разрешить перезапись существующего подключения.
        :return: None.

        :raises SystemError: Если клиент уже инициализирован.
        """
        if cls._connection is not None:
            if not has_set:
                raise SystemError("RabbitMQ клиент уже инициализирован.")
            else:
                return

        cls._connection = await connect_robust(
            url=url,
            timeout=timeout,
            loop=asyncio.get_event_loop(),
        )
        cls._channel = await cls._connection.channel()
        await cls._channel.set_qos(prefetch_count=10)
        cls._queue_name = queue_name
        # await cls._create_queue(queue_name)

        cls._is_connected = True
        logger.info("RabbitMQ клиент инициализирован.")

    @classmethod
    async def create_queue(cls, conversation_id: UUID) -> None:
        """
        Создание очереди для конкретного диалога в RabbitMQ.

        :param conversation_id: Идентификатор диалога.
        """
        if not cls._is_connected:
            raise SystemError("RabbitMQ клиент не инициализирован.")
        queue_name = f"{cls._queue_name}_{conversation_id}"
        await cls._channel.declare_queue(
            name=queue_name,
            durable=True,
            auto_delete=False,
            exclusive=False,
        )
        cls._queue_name = queue_name
        logger.info(f"Очередь '{queue_name}' успешно создана/проверена.")

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
            routing_key: str | None = None,
            persistent: bool = True,
            priority: int | None = None,
            expiration: int | None = None,
            message_id: str | None = None,
            headers: dict[str, Any] | None = None,
    ) -> None:
        """
        Отправка сообщения в очередь.

        :param body: Тело сообщения.

        :param routing_key: Ключ маршрутизации
            (если None, используется имя очереди).

        :param persistent: Если True, сообщение будет сохранено на диск.

        :param priority: Приоритет сообщения (0-9).

        :param expiration: TTL сообщения в миллисекундах.

        :param message_id: Идентификатор сообщения.

        :param headers: Дополнительные заголовки сообщения.

        :return: None.

        :raises RabbitMQPublishError: Если сообщение не отправлено.

        :raises SystemError: Если клиент не инициализирован или
            очередь не создана.
        """
        if not cls._is_connected or cls._channel is None:
            raise SystemError("RabbitMQ клиент не инициализирован.")

        if cls._queue_name is None:
            raise SystemError(
                "Очередь не создана. Убедитесь, что метод setup() был вызван "
                "с auto_create_queue=True"
            )

        if priority is not None and not (0 <= priority <= 9):
            raise ValueError(
                "Значение параметра priority должно быть от 0 до 9."
            )

        delivery_mode = DeliveryMode.PERSISTENT \
            if persistent \
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
            routing_key = routing_key or cls._queue_name

            await cls._channel.default_exchange.publish(
                message,
                routing_key=routing_key
            )

            logger.info(
                f"Сообщение успешно отправлено в очередь '{routing_key}'.",
                message_id=message_id,
                persistent=persistent,
                priority=priority
            )

        except Exception as err:
            logger.error(
                f"Ошибка публикации сообщения в RabbitMQ: "
                f"{err} ({err.__class__.__name__})",
                queue_name=cls._queue_name,
                message_id=message_id,
            )
            raise errors.RabbitMQPublishError(
                str(err),
                "default_exchange",
                cls._queue_name
            )
        else:
            logger.success(
                f"Сообщение отправлено в очередь '{routing_key}'."
            )
