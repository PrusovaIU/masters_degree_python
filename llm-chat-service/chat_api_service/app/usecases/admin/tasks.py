from uuid import UUID

from celery.result import AsyncResult

from chat_api_service.app.tasks.llm_tasks import llm_request
from libs.schemas.llm import CeleryTaskResponse


class TasksUsecase:
    @staticmethod
    def task_status(task_id: UUID) -> CeleryTaskResponse:
        """
        Получение статуса сообщения.

        :param task_id: ID задачи.
        :return: Статус сообщения.

        :raises TaskNotFound: Задача не найдена.
        """
        task_result = AsyncResult(str(task_id), app=llm_request.app)
        response = CeleryTaskResponse(
            result=task_result.result,
            status=task_result.status,
            traceback=task_result.traceback
        )
        return response
