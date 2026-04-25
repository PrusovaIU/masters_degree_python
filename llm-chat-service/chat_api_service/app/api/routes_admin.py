from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from libs.schemas.error_detail import Detail
from .deps.jwt import AdminDep
from chat_api_service.app.schemas.llm import CeleryTaskResponse
from .deps.usecases import TasksUsecaseDep
from ..core.exceptions.task import TaskNotFound

router_admin = APIRouter(prefix="/admin", tags=["admin"])


@router_admin.get(
    "/tasks/{task_id}/status",
    response_model=CeleryTaskResponse,
    summary="Получение статуса задачи LLM",
    description="Получение статуса задачи обработки запроса к LLM.",
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": Detail
        }
    }

)
def get_llm_task_status(
        task_id: UUID,
        admin_user: AdminDep,
        tasks_usecase: TasksUsecaseDep
) -> CeleryTaskResponse:
    """
    Получение статуса задачи LLM.

    :param task_id: UUID задачи Celery.
    :param admin_user: Аутентифицированный пользователь с ролью администратора.
    :param tasks_usecase: Usecase для работы с задачами.

    :return: Статус задачи.
    """
    try:
        task_status: CeleryTaskResponse = tasks_usecase.task_status(task_id)
    except TaskNotFound as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=err.detail_jsonable_encoder
        )
    return task_status
