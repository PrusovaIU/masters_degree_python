from .base import AppException


class RabbitMQException(AppException):
    """Ошибка при работе с RabbitMQ"""
    pass


class RabbitMQPublishError(RabbitMQException):
    """Ошибка при публикации сообщения в очередь"""
    def __init__(self, message, exchange_name: str, routing_key: str):
        super().__init__(
            message,
            exchange_name=exchange_name,
            routing_key=routing_key
        )
        self._exchange_name = exchange_name
        self._routing_key = routing_key

    @property
    def exchange_name(self):
        return self._exchange_name

    @property
    def routing_key(self):
        return self._routing_key
