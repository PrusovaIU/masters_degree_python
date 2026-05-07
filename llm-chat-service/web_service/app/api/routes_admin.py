from .deps.usecases import AdminUsecaseDep


from uuid import UUID

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse

from web_service.app.api.deps.current_user import AdminTokenDep
from libs.schemas.llm import CeleryTaskResponse
from web_service.app.core.exceptions.chat_api_client import AccessException, TaskNotFoundException
from libs.schemas.conversation import ConversationListResponse
from libs.schemas.pagination import PaginationRequest


router_admin = APIRouter(prefix="/admin")


class Templates:
    INDEX = "admin/index.html"


@router_admin.get(
    "/",
    response_class=HTMLResponse,
    include_in_schema=False
)
async def admin_page(
        request: Request,
        admin_token: AdminTokenDep
):
    """
    :param request: Заппрос пользователя.
    :param admin_token: Проверка токена админа.
    :return: Страница админки.
    """
    return request.app.state.settings.jinja.templates.TemplateResponse(
        request=request,
        name=Templates.INDEX,
        context={"settings": request.app.state.settings}
    )


@router_admin.get(
    "/tasks/{task_id}/status",
    response_model=CeleryTaskResponse,
    include_in_schema=False
)
async def get_task_status(
        admin_token: AdminTokenDep,
        usecase: AdminUsecaseDep,
        task_id: UUID
):
    """
    Получение статуса задачи.

    :param admin_token: Проверка токена админа.
    :param usecase: Usecase для работы с админкой.
    :param task_id: Идентификатор задачи.
    :return: Статус задачи.
    """
    try:
        return await usecase.get_task_status(admin_token, task_id)
    except AccessException as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(err)
        )
    except TaskNotFoundException as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err)
        )


@router_admin.post(
    "/conversation/all",
    response_model=ConversationListResponse,
    include_in_schema=False
)
async def get_all_conversations(
        admin_token: AdminTokenDep,
        usecase: AdminUsecaseDep,
        pagination: PaginationRequest

) -> ConversationListResponse:
    """
    Получение всех диалогов для админки.

    :param admin_token: Access token админа.
    :param usecase: Usecase для работы с админкой.
    :param pagination: Данные для пагинации.
    :return: Список диалогов.
    """
    try:
        return await usecase.get_all_conversations(
            admin_token,
            pagination.limit,
            pagination.offset
        )
    except AccessException as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(err)
        )
