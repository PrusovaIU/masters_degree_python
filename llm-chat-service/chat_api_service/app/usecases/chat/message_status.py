from celery.result import AsyncResult

from chat_api_service.app.db.models import Message
from chat_api_service.app.repositories.message import MessageRepository
from chat_api_service.app.core.exceptions.conversation import (
    ConversationAccessDenied)
from chat_api_service.app.consts.llm_tasks import LLMTasksStatus
from chat_api_service.app.schemas.llm import LLMStatusResponse
from chat_api_service.app.tasks.llm_tasks import llm_request
from chat_api_service.app.core.exceptions.message import MessageNotFound


class MessageStatusUsecase:
    def __init__(
            self,
            message_repository: MessageRepository,
            task_id: str,
            user_id: str
    ):
        self._msg_repo = message_repository
        self._task_id = task_id
        self._user_id = user_id

    async def execute(self) -> LLMStatusResponse:
        """
        Получение статуса сообщения.

        :return: Статус сообщения.

        :raises MessageNotFound: Если сообщение не найдено.
        :raises ConversationAccessDenied: Если доступ к диалогу запрещен.
        """
        message: Message | None = await self._msg_repo.get_by_llm_task_id(
            self._task_id
        )
        if not message:
            raise MessageNotFound(
                "Сообщение не найдено",
                f"task_id={self._task_id}"
            )
        if message.conversation.user_id != self._user_id:
            raise ConversationAccessDenied(
                f"Доступ для пользователя запрещен",
                message.conversation_id,
                self._user_id
            )
        task_result = AsyncResult(self._task_id, app=llm_request.app)
        task_status = LLMTasksStatus.get_status(task_result.state)
        response = LLMStatusResponse(
            task_id=self._task_id,
            status=task_status,
            message_id=message.id,
            conversation_id=message.conversation_id,
            created_at=message.created_at,
            updated_at=message.updated_at
        )
        response.enrich(task_result)
        return response
