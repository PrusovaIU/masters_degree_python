from uuid import UUID

from web_service.app.services.chat_client import ChatAPIServiceClient
from libs.schemas.llm import LLMTaskStatusSchema


class AdminUsecase:
    def __init__(self, chat_client: ChatAPIServiceClient):
        self._chat_client = chat_client

    async def get_task_status(self, task_id: UUID) -> LLMTaskStatusSchema:
        """
        Получить статус задачи.

        :param task_id: Идентификатор задачи.
        :return: Статус задачи.
        """
        return await self._chat_client.admin_task_status(task_id)
