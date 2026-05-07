from uuid import UUID

from libs.schemas.conversation import ConversationListResponse
from libs.schemas.llm import CeleryTaskResponse
from web_service.app.services.chat_client import ChatAPIServiceClient


class AdminUsecase:
    def __init__(self, chat_client: ChatAPIServiceClient):
        self._chat_client = chat_client

    async def get_task_status(
            self,
            access_token: str,
            task_id: UUID
    ) -> CeleryTaskResponse:
        """
        Получить статус задачи.

        :param access_token: Токен доступа.
        :param task_id: Идентификатор задачи.
        :return: Статус задачи.

        :raise AccessException: Если доступ запрещен.
        :raise TaskNotFoundException: Если задача не найдена.
        :raise GetTaskStatusException: В случае ошибки получения статуса.
        """
        return await self._chat_client.admin_task_status(access_token, task_id)

    async def get_all_conversations(
            self,
            access_token: str,
            limit: int = 100,
            offset: int = 0
    ) -> ConversationListResponse:
        """
        Получить список всех диалогов для админа.

        :param access_token: Access token.
        :param limit: Лимит записей на странице.
        :param offset: Смещение.
        :return: Список диалогов.

        :raise AccessException: Если доступ запрещен.
        :raise GetConversationException: В случае ошибки получения списка.
        """
        return await self._chat_client.admin_conversation_all(
            access_token, limit, offset
        )
