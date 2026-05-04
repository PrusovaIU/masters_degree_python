from uuid import UUID

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse

from web_service.app.api.deps.current_user import AccessTokenDep
from web_service.app.api.deps.usecases import ChatUsecaseDep
from web_service.app.api.login_redirect import LOGIN_REDIRECT
from web_service.app.core.exceptions import chat_api_client as errors
from web_service.app.schemas.config import Settings
from libs.schemas.conversation import ConversationHistoryResponse
from loguru import logger

router_conversation = APIRouter(prefix="/conversation")


class Templates:
    CONVERSATION_LIST = "chat/conversation/index.html"
    NEW_CONVERSATION = "chat/conversation/new.html"
    MESSAGE_HISTORY = "chat/conversation/history.html"


@router_conversation.get(
    "/all",
    response_class=HTMLResponse,
    include_in_schema=False
)
async def conversations_list_page(
        request: Request,
        access_token: AccessTokenDep,
        usecase: ChatUsecaseDep,
        limit: int = 10,
        page: int = 1,
        created: bool = False
):
    """Главная страница чата — список диалогов"""
    conversations, total_pages, total = await usecase.conversation_all(
        access_token, limit, page
    )
    conversations: dict[UUID, str]

    return request.app.state.settings.jinja.templates.TemplateResponse(
        request=request,
        name=Templates.CONVERSATION_LIST,
        context={
            "settings": request.app.state.settings,
            "conversations": conversations,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "created": created
        }
    )


@router_conversation.get(
    "/new",
    response_class=HTMLResponse,
    include_in_schema=False
)
async def new_conversation_page(
        request: Request,
        access_token: AccessTokenDep
):
    """Страница создания нового диалога"""
    return request.app.state.settings.jinja.templates.TemplateResponse(
        request=request,
        name=Templates.NEW_CONVERSATION,
        context={"settings": request.app.state.settings}
    )


@router_conversation.post(
    "/new",
    response_class=HTMLResponse,
    include_in_schema=False
)
async def new_conversation(
        request: Request,
        access_token: AccessTokenDep,
        usecase: ChatUsecaseDep,
        title: str
):
    """
    Создание нового диалога.

    :param request: Запрос пользователя.
    :param access_token: Access token пользователя.
    :param usecase: Usecase для работы с диалогами.
    :param title: Заголовок диалога.
    """
    try:
        await usecase.new_conversation(access_token, title)
    except Exception as err:
        context = {
            "settings": request.app.state.settings,
            "error": str(err)
        }
        response = request.app.state.settings.jinja.templates.TemplateResponse(
            request=request,
            name=Templates.NEW_CONVERSATION,
            context=context,
            status_code=status.HTTP_502_BAD_GATEWAY
        )
    else:
        response = RedirectResponse(
            url=f"{Templates.CONVERSATION_LIST}?created=true",
            status_code=status.HTTP_302_FOUND
        )
    return response


@router_conversation.get(
    "/{conversation_id}",
    response_class=HTMLResponse,
    include_in_schema=False
)
async def conversation_page(
        request: Request,
        access_token: AccessTokenDep,
        usecase: ChatUsecaseDep,
        conversation_id: UUID,
        limit: int = 10,
        page: int = 1
):
    """Страница диалога"""
    settings: Settings = request.app.state.settings
    try:
        messages, total_pages, total = await usecase.conversation_history(
            access_token, conversation_id, limit, page
        )
    except Exception as err:
        match type(err):
            case errors.AccessException:
                status_code = status.HTTP_403_FORBIDDEN
            case errors.ConversationNotFoundException:
                status_code = status.HTTP_404_NOT_FOUND
            case _:
                status_code = status.HTTP_502_BAD_GATEWAY
        context = {
            "settings": settings,
            "error": str(err),
            "messages": {},
            "limit": limit,
            "page": page,
            "total_pages": 0,
            "total": 0,
        }
        response = settings.jinja.templates.TemplateResponse(
            request=request,
            name=Templates.MESSAGE_HISTORY,
            context=context,
            status_code=status_code
        )
    else:
        context = {
            "settings": settings,
            "messages": messages,
            "limit": limit,
            "page": page,
            "total_pages": total_pages,
            "total": total,
        }
        response = settings.jinja.templates.TemplateResponse(
            request=request,
            name=Templates.MESSAGE_HISTORY,
            context=context,
            status_code=status.HTTP_302_FOUND
        )
    return response


@router_conversation.post(
    "/{conversation_id}/query",
    response_class=HTMLResponse,
    include_in_schema=False
)
async def conversation_query(
        request: Request,
        access_token: AccessTokenDep,
        usecase: ChatUsecaseDep,
        conversation_id: UUID,
        content: str,
        temperature: float = 0.7
):
    """
    Отправка сообщения в диалог.

    :param request: Запрос пользователя.
    :param access_token: Access token пользователя.
    :param usecase: Usecase для работы с диалогами.
    :param conversation_id: Идентификатор диалога.
    :param content: Содержимое сообщения.
    :param temperature: Температура генерации ответа.
    """
    settings: Settings = request.app.state.settings
    try:
        message_id: UUID = await usecase.send_message(
            access_token, conversation_id, content, temperature
        )
    except Exception as err:
        logger.trace(err)
        match type(err):
            case errors.AccessException:
                status_code = status.HTTP_403_FORBIDDEN
            case errors.ConversationNotFoundException:
                status_code = status.HTTP_404_NOT_FOUND
            case _:
                status_code = status.HTTP_502_BAD_GATEWAY
        context = {
            "settings": settings,
            "error": str(err)
        }
        response = settings.jinja.templates.TemplateResponse(
            request=request,
            name=Templates.MESSAGE_HISTORY,
            context=context,
            status_code=status_code
        )
    else:
        response = JSONResponse(
            content={"message_id": str(message_id)}
        )
    return response
