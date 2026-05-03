from fastapi import Request, Response, status, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction
import logging

from starlette.types import ASGIApp

from web_service.app.schemas.config import AuthCookieSettings

logger = logging.getLogger(__name__)


class AuthCookieMiddleware(BaseHTTPMiddleware):
    """Middleware для автоматической подстановки токенов из cookie"""

    async def dispatch(self, request: Request, call_next):
        state = request.app.state
        if (
                request.url.path.startswith(state.static_url) or
                request.url.path in ("/", "/health", "/auth/login")
        ):
            return await call_next(request)

        access_token: str | None = request.cookies.get(
            state.access_token_cookie_name
        )
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized"
            )

        request.state.access_token = access_token
        request.state.is_authenticated = True

        response = await call_next(request)
        return response


def set_auth_cookies(
        response: Response,
        access_token: str,
        refresh_token: str,
        access_expires: int,
        refresh_expires: int,
        cookie_settings: AuthCookieSettings
) -> None:
    """
    Установка cookie с токенами авторизации.

    :param response: Response - объект ответа FastAPI;
    :param access_token: access токен;
    :param refresh_token: refresh токен;
    :param access_expires: время жизни access токена;
    :param refresh_expires: время жизни refresh токена.
    :param cookie_settings: Настройки cookie.

    :returns: None.
    """
    cookie_params = {
        "httponly": True,
        "secure": cookie_settings.token_cookie_secure,
        "samesite": cookie_settings.cookie_same_site,
        "path": "/",
    }

    response.set_cookie(
        key=cookie_settings.access_token_cookie_name,
        value=access_token,
        max_age=access_expires,
        **cookie_params
    )
    response.set_cookie(
        key=cookie_settings.refresh_token_cookie_name,
        value=refresh_token,
        max_age=refresh_expires,
        **cookie_params
    )


def clear_auth_cookies(
        response: Response,
        cookie_settings: AuthCookieSettings
) -> None:
    """
    Очистка cookie авторизации.

    :param response: Response - объект ответа FastAPI.
    :param cookie_settings: Настройки cookie.
    :returns: None.
    """
    response.delete_cookie(
        cookie_settings.access_token_cookie_name,
        path="/"
    )
    response.delete_cookie(
        cookie_settings.refresh_token_cookie_name,
        path="/"
    )
