from uuid import UUID

from loguru import logger

from chat_api_service.app.core.exceptions import message as errors
from chat_api_service.app.core.exceptions.message import (MessageNotFound,
                                                          UpdateMessageError)
from chat_api_service.app.db.models import Message
from chat_api_service.app.repositories.conversation import \
    ConversationRepository
from chat_api_service.app.repositories.message import MessageRepository
from libs.consts.message import MessageStatus


class MessageUsecase:
    """
    Usecase для работы сообщениями.

    :param message_repository: Репозиторий сообщений.
    :param conversation_repository: Репозиторий диалогов.
    """
    def __init__(
            self,
            message_repository: MessageRepository,
            conversation_repository: ConversationRepository
    ):
        self._msg_repo = message_repository
        self._conv_repo = conversation_repository

    async def _check_message_access(
            self,
            message: Message | None,
            message_id: UUID | str,
            user_id: str
    ) -> None:
        """
        Проверка доступа пользователя к сообщению.

        :param message: Сообщение.
        :param message_id: Идентификатор сообщения.
        :param user_id: Идентификатор пользователя.
        :return: None.

        :raises MessageNotFound: Если сообщение не найдено.

        :raises ConversationAccessDenied: Если доступ к диалогу запрещен.
        """
        if not message:
            logger.warning(f"Сообщение не найдено: {message_id}")
            raise MessageNotFound(
                "Сообщение не найдено",
                message_id=message_id
            )
        await self._conv_repo.get(message.conversation_id, user_id)

    async def status_update(
            self,
            message_id: UUID,
            user_id: str,
            new_status: MessageStatus
    ) -> Message:
        """
        Обновление статуса сообщения.

        :param message_id: Идентификатор сообщения.
        :param user_id: Идентификатор пользователя.
        :param new_status: Новый статус сообщения.
        :return: Обновленное сообщение.

        :raises MessageNotFound: Если сообщение не найдено.
        :raises ConversationAccessDenied: Если доступ к диалогу запрещен.
        :raises UpdateMessageError: Если сообщение не было обновлено.
        :raises InvalidMessageStatus: Если новый статус сообщения не валидный.
        """
        message: Message | None = await self._msg_repo.get_by_id(message_id)
        await self._check_message_access(
            message,
            message_id,
            user_id
        )
        new_message: Message = await self._msg_repo.update_status(
            message_id,
            new_status
        )
        if not new_message:
            logger.warning(
                f"Ошибка обновления статуса сообщения: {message_id} "
                f"(сообщение не было возвращено)"
            )
            raise UpdateMessageError(
                f"Ошибка обновления статуса сообщения",
                message_id=message_id
            )
        return new_message

    async def get_by_id(self, message_id: UUID, user_id: str) -> Message:
        """
        Получение сообщения по идентификатору.

        :param message_id: Идентификатор сообщения.
        :param user_id: Идентификатор пользователя.
        :return: Сообщение.

        :raises MessageNotFound: Если сообщение не найдено.
        :raises ConversationAccessDenied: Если доступ к диалогу запрещен.
        """
        message: Message = await self._msg_repo.get_by_id(message_id)
        if not message:
            raise errors.MessageNotFound(
                "Сообщение не найдено", message_id
            )
        await self._check_message_access(
            message,
            message_id,
            user_id
        )
        return message
