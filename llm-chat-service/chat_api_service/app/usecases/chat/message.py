from uuid import UUID

from celery.result import AsyncResult

from chat_api_service.app.consts.message import MessageStatus
from chat_api_service.app.db.models import Message
from chat_api_service.app.repositories.conversation import \
    ConversationRepository
from chat_api_service.app.repositories.message import MessageRepository
from chat_api_service.app.core.exceptions.conversation import (
    ConversationAccessDenied)
from chat_api_service.app.consts.llm_tasks import LLMTasksStatus
from chat_api_service.app.schemas.llm import LLMStatusResponse
from chat_api_service.app.tasks.llm_tasks import llm_request
from chat_api_service.app.core.exceptions.message import MessageNotFound, UpdateMessageError
from loguru import logger


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

    async def get_by_task_id(
            self,
            task_id: str,
            user_id: str
    ) -> LLMStatusResponse:
        """
        Получение статуса сообщения.

        :param task_id: ID задачи.
        :param user_id: ID пользователя.
        :return: Статус сообщения.

        :raises MessageNotFound: Если сообщение не найдено.
        :raises ConversationAccessDenied: Если доступ к диалогу запрещен.
        """
        message: Message | None = await self._msg_repo.get_by_llm_task_id(
            task_id
        )
        await self._check_message_access(
            message,
            f"task_id={task_id}",
            user_id
        )
        task_result = AsyncResult(task_id, app=llm_request.app)
        task_status = LLMTasksStatus.get_status(task_result.state)
        response = LLMStatusResponse(
            task_id=task_id,
            status=task_status,
            message_id=message.id,
            conversation_id=message.conversation_id,
            created_at=message.created_at,
            updated_at=message.updated_at
        )
        response.enrich(task_result)
        return response

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
        :raises ValueError: Если назначить сообщению указанный статус.
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
