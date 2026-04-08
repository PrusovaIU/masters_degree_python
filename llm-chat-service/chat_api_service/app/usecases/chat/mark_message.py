from datetime import datetime
from uuid import UUID

from chat_api_service.app.consts.message import MessageStatus
from chat_api_service.app.db.models import Message
from chat_api_service.app.repositories.message import MessageRepository
import loguru
from chat_api_service.app.core.exceptions.message import MessageNotFound


class MarkMessageUsecase:
    """
    Usecase для изменения статуса сообщения.
    """
    def __init__(
            self,
            message_repository: MessageRepository,
            logger = None
    ):
        self._repo = message_repository
        self._logger = logger if logger else loguru.logger

    async def as_read(
            self,
            message_id: UUID,
            user_id: str,
    ) -> datetime | None:
        """
        Пометить сообщение как прочитанное.

        :param message_id: ID сообщения.
        :param user_id: ID пользователя.

        :return: Дата и время прочтения сообщения.
        """
        message: Message | None = await self._repo.get_by_id(message_id)
        if not message:
            raise MessageNotFound("Сообщение не найдено", message_id)
        if message.conversation.user_id != user_id:
            raise MessageNotFound(
                "Не найдено сообщение для данного пользователя",
                message_id
            )
        await self._repo.update_status(message_id, MessageStatus.READ)
        self._logger.info(
            f"Сообщение {message_id} помечено как прочитанное "
            f"пользователем {user_id}"
        )
        return message.read_at
