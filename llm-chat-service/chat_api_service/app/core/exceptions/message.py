from uuid import UUID

from .base import AppException
from chat_api_service.app.consts.message import MessageStatus


class InvalidMessageStatus(AppException):
    """Ошибка при изменении статуса сообщения."""
    def __init__(
            self,
            message: str,
            old_status: MessageStatus | str,
            new_status: MessageStatus | str
    ):
        super().__init__(message, old_status=old_status, new_status=new_status)
        self._old_status = old_status
        self._new_status = new_status

    @property
    def old_status(self) -> MessageStatus:
        """Старый статус сообщения."""
        return self._old_status

    def new_status(self) -> MessageStatus:
        """Новый статус сообщения."""
        return self._new_status


class MessageNotFound(AppException):
    """Сообщение не найдено."""
    def __init__(self, message: str, message_id: str | UUID):
        super().__init__(message, message_id=message_id)
        self._message_id = message_id

    @property
    def message_id(self) -> UUID:
        """ID сообщения."""
        return self._message_id
