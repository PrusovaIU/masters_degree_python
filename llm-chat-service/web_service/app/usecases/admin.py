from uuid import UUID

from web_service.app.services.chat_client import ChatAPIServiceClient
from libs.schemas.llm import LLMTaskStatusSchema


class AdminUsecase:
    def __init__(self, chat_client: ChatAPIServiceClient):
        self._chat_client = chat_client

    async def get_task_status(
            self,
            access_token: str,
            task_id: UUID
    ) -> LLMTaskStatusSchema:
        """
        Получить статус задачи.

        :param access_token: Токен доступа.
        :param task_id: Идентификатор задачи.
        :return: Статус задачи.

        :raise AccessException: Если доступ запрещен.
        :raise GetTaskStatusException: В случае ошибки получения статуса.
        """
        return await self._chat_client.admin_task_status(access_token, task_id)
