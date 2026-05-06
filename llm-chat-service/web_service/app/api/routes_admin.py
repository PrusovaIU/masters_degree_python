from .deps.usecases import AdminUsecaseDep


from uuid import UUID

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse

from web_service.app.api.deps.current_user import AdminTokenDep
from web_service.app.api.deps.usecases import ChatUsecaseDep, StreamChatUsecaseDep
from web_service.app.core.exceptions import chat_api_client as errors
from web_service.app.schemas.config import Settings
from loguru import logger
from libs.schemas.conversation import ConversationHistoryBeforeResponse


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
    return request.app.state.settings.jinja.templates.TemplateResponse(
        request=request,
        name=Templates.INDEX,
        context={"settings": request.app.state.settings}
    )

