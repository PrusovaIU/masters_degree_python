from fastapi import APIRouter, Request, Form, status, Depends
from fastapi.responses import RedirectResponse, HTMLResponse

from libs.schemas.auth import LoginResponse, RegisterResponse
from libs.schemas.user import UserPublic
from web_service.app.core.security import set_auth_cookies
from web_service.app.services.auth_client import AuthClient
from .deps.usecases import AuthUsecaseDep
from web_service.app.core.exceptions import auth_client as errors
from web_service.app.schemas.config import Settings
from web_service.app.core.exceptions import auth_usecase as usecase_errors


router_auth = APIRouter()


@router_auth.get(
    "/auth/login",
    response_class=HTMLResponse,
    include_in_schema=False
)
async def login_page(
        request: Request,
        auth_usecase: AuthUsecaseDep,
        registered: bool = False
):
    """Страница входа"""
    user: UserPublic | None = await auth_usecase.get_user_data(request)
    if user:
        return RedirectResponse(
            url="/chat",
            status_code=status.HTTP_302_FOUND
        )
    return request.app.state.settings.jinja.templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={
            "settings": request.app.state.settings,
            "registered": registered
        }
    )


@router_auth.post(
    "/auth/login",
    response_class=HTMLResponse,
    include_in_schema=False
)
async def login_process(
        request: Request,
        auth_usecase: AuthUsecaseDep,
        username: str = Form(),
        password: str = Form(),
        remember: bool = Form(False)
):
    """
    Обработка POST-запроса с формой входа
    """
    settings: Settings = request.app.state.settings
    try:
        login_data: LoginResponse = await auth_usecase.auth(
            username, password
        )
    except errors.LoginError as err:
        context = {
            "settings": settings,
            "error": str(err),
            "form_data": {"username": username}
        }
        response = settings.jinja.templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context=context,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    else:
        response = RedirectResponse(
            url="/chat",
            status_code=status.HTTP_302_FOUND
        )
        set_auth_cookies(
            response,
            settings.auth_cookie,
            login_data.access_token,
            login_data.expires_in if remember else None,
            login_data.refresh_token,
            login_data.refresh_expires_in if remember else None
        )
    return response


@router_auth.get(
    "/auth/register",
    response_class=HTMLResponse,
    include_in_schema=False
)
async def register_page(
        request: Request,
        auth_usecase: AuthUsecaseDep
):
    """Страница регистрации"""
    user: UserPublic | None = await auth_usecase.get_user_data(request)
    if user:
        return RedirectResponse(
            url="/chat",
            status_code=status.HTTP_302_FOUND
        )
    return request.app.state.settings.jinja.templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context={"settings": request.app.state.settings}
    )


@router_auth.post("/auth/register", include_in_schema=False)
async def register_submit(
        request: Request,
        auth_usecase: AuthUsecaseDep,
        email: str = Form(),
        password: str = Form(),
        password_confirm: str = Form()
):
    """Обработка формы регистрации"""
    settings: Settings = request.app.state.settings
    try:
        await auth_usecase.register(
            email, password, password_confirm
        )
    except usecase_errors.PasswordNotMatchException as err:
        context = {
            "settings": settings,
            "error": str(err)
        }
        response = settings.jinja.templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context=context,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except errors.UserAlreadyExistsError as err:
        context = {
            "settings": settings,
            "error": str(err)
        }
        response = settings.jinja.templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context=context,
            status_code=status.HTTP_409_CONFLICT
        )
    else:
        response = RedirectResponse(
            url="/auth/login?registered=True",
            status_code=status.HTTP_302_FOUND
        )
    return response
#
#
# @router.get("/auth/logout", include_in_schema=False)
# async def logout(request: Request):
#     """Выход из системы"""
#     response = RedirectResponse(url="/auth/login",
#                                 status_code=status.HTTP_302_FOUND)
#     clear_auth_cookies(response)
#     return response