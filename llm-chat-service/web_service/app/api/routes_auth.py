from fastapi import APIRouter, Request, Form, status, Depends
from fastapi.responses import RedirectResponse, HTMLResponse

from libs.schemas.auth import LoginResponse
from libs.schemas.user import UserPublic
from web_service.app.core.security import set_auth_cookies
from web_service.app.services.auth_client import AuthClient
from .deps.usecases import AuthUsecaseDep
from web_service.app.core.exceptions import auth_client as errors
from ..schemas.config import Settings

router_auth = APIRouter()


@router_auth.get(
    "/auth/login",
    response_class=HTMLResponse,
    include_in_schema=False
)
async def login_page(
        request: Request,
        auth_usecase: AuthUsecaseDep
):
    """Страница входа"""
    user: UserPublic | None = await auth_usecase.auth_page(request)
    if user:
        return RedirectResponse(
            url="/chat",
            status_code=status.HTTP_302_FOUND
        )
    return request.app.state.settings.jinja.templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={"settings": request.app.state.settings}
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
            login_data.expires_in,
            login_data.refresh_token,
            login_data.refresh_expires_in
        )
    return response


# @router_auth.post("/auth/login", include_in_schema=False)
# async def login_submit(
#         request: Request,
#         username: str = Form(),
#         password: str = Form()
# ):
#     """Обработка формы входа"""
#     client = AuthClient()
#     result = await client.login(username, password)
#
#     if result:
#         response = RedirectResponse(url="/chat",
#                                     status_code=status.HTTP_302_FOUND)
#         set_auth_cookies(
#             response,
#             access_token=result.access_token,
#             refresh_token=result.refresh_token,
#             access_expires=result.expires_in,
#             refresh_expires=result.refresh_expires_in
#         )
#         return response
#
#     return templates.TemplateResponse(
#         "auth/login.html",
#         {"request": request, "error": "Неверный email или пароль"},
#         status_code=status.HTTP_401_UNAUTHORIZED
#     )
#
#
# @router.get("/auth/register", response_class=HTMLResponse,
#             include_in_schema=False)
# async def register_page(request: Request):
#     """Страница регистрации"""
#     user = await get_authenticated_user(request)
#     if user:
#         return RedirectResponse(url="/chat", status_code=status.HTTP_302_FOUND)
#     return templates.TemplateResponse("auth/register.html",
#                                       {"request": request})
#
#
# @router.post("/auth/register", include_in_schema=False)
# async def register_submit(
#         request: Request,
#         email: str = Form(...),
#         password: str = Form(...),
#         password_confirm: str = Form(...)
# ):
#     """Обработка формы регистрации"""
#     if password != password_confirm:
#         return templates.TemplateResponse(
#             "auth/register.html",
#             {"request": request, "error": "Пароли не совпадают"},
#             status_code=status.HTTP_400_BAD_REQUEST
#         )
#
#     client = AuthClient()
#     result = await client.register(
#         RegisterRequest(email=email, password=password))
#
#     if result:
#         return RedirectResponse(url="/auth/login?registered=1",
#                                 status_code=status.HTTP_302_FOUND)
#
#     return templates.TemplateResponse(
#         "auth/register.html",
#         {"request": request,
#          "error": "Пользователь с таким email уже существует"},
#         status_code=status.HTTP_409_CONFLICT
#     )
#
#
# @router.get("/auth/logout", include_in_schema=False)
# async def logout(request: Request):
#     """Выход из системы"""
#     response = RedirectResponse(url="/auth/login",
#                                 status_code=status.HTTP_302_FOUND)
#     clear_auth_cookies(response)
#     return response