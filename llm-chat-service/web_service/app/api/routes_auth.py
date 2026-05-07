from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse, HTMLResponse

from libs.schemas.auth import LoginResponse
from libs.schemas.user import UserPublic
from ..core.cookie import set_auth_cookies, set_user_cookie, clear_auth_cookies
from .deps.usecases import AuthUsecaseDep
from web_service.app.core.exceptions import auth_client as errors
from web_service.app.schemas.config import Settings
from web_service.app.core.exceptions import auth_usecase as usecase_errors
from .deps.current_user import AccessTokenDep
from .login_redirect import LOGIN_REDIRECT


router_auth = APIRouter(prefix="/auth")


@router_auth.get(
    "/login",
    response_class=HTMLResponse,
    include_in_schema=False
)
async def login_page(
        request: Request,
        access_token: AccessTokenDep,
        registered: bool = False
):
    """Страница входа"""
    if access_token:
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
    "/login",
    response_class=HTMLResponse,
    include_in_schema=False
)
async def login_process(
        request: Request,
        auth_usecase: AuthUsecaseDep,
        username: str = Form(),
        password: str = Form()
):
    """
    Обработка POST-запроса с формой входа
    """
    settings: Settings = request.app.state.settings
    try:
        login_data: LoginResponse = await auth_usecase.auth(
            username, password
        )
        me_data: UserPublic = await auth_usecase.me(login_data.access_token)
    except errors.LoginError:
        context = {
            "settings": settings,
            "error": "Неверный логин или пароль",
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
            login_data.expires_in,
            login_data.refresh_token,
            login_data.refresh_expires_in
        )
        set_user_cookie(
            response,
            settings.cookie,
            me_data,
            login_data.expires_in
        )
    return response


@router_auth.get(
    "/register",
    response_class=HTMLResponse,
    include_in_schema=False
)
async def register_page(
        request: Request,
        access_token: AccessTokenDep
):
    """Страница регистрации"""
    if access_token:
        return RedirectResponse(
            url="/chat",
            status_code=status.HTTP_302_FOUND
        )
    return request.app.state.settings.jinja.templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context={"settings": request.app.state.settings}
    )


@router_auth.post("/register", include_in_schema=False)
async def register_submit(
        request: Request,
        auth_usecase: AuthUsecaseDep,
        email: str = Form(),
        password: str = Form(),
        password_confirm: str = Form()
):
    """
    Обработка запроса регистрации.

    :param request: Запрос пользователя.
    :param auth_usecase: Usecase для авторизации.
    :param email: Электронная почта пользователя.
    :param password: Пароль пользователя.
    :param password_confirm: Подтверждение пароля.
    """
    settings: Settings = request.app.state.settings
    try:
        await auth_usecase.register(
            email, password, password_confirm
        )
    except usecase_errors.PasswordNotMatchException:
        context = {
            "settings": settings,
            "error": "Пароли не совпадают"
        }
        response = settings.jinja.templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context=context,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except errors.UserAlreadyExistsError:
        context = {
            "settings": settings,
            "error": f"Пользователь \"{email}\" уже существует"
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


@router_auth.get("/logout", include_in_schema=False)
async def logout(request: Request):
    """Выход из системы"""
    settings: Settings = request.app.state.settings
    response = LOGIN_REDIRECT
    clear_auth_cookies(response, settings)
    return response