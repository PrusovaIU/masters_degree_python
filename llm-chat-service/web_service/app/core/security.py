from datetime import datetime

from fastapi import Request, Response, status, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction
from web_service.app.services.auth_client import AuthClient
from libs.schemas.auth import RefreshTokenResponse
from loguru import logger
from .exceptions.security import NotAuthenticated
from libs.schemas.user import UserPublic

from web_service.app.schemas.config import AuthCookieSettings, Settings, CookieSettings
from web_service.app.api.login_redirect import LOGIN_REDIRECT
from libs.jwt_token import get_access_payload, AccessTokenData
from web_service.app.schemas.user import User


def set_access_token_cookie(
        response: Response,
        settings: AuthCookieSettings,
        access_token: str,
        expires_in: int | None
) -> None:
    """
    Установка cookie с access токеном.

    :param response: Ответ на запрос;
    :param settings: Настройки cookie;
    :param access_token: Access токен;
    :param expires_in: Время жизни токена;
    :return: None
    """
    response.set_cookie(
        key=settings.access_token_cookie_name,
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_same_site,
        max_age=expires_in
    )


def set_refresh_token_cookie(
        response: Response,
        settings: AuthCookieSettings,
        refresh_token: str,
        expires_in: int | None
) -> None:
    """
    Установка cookie с refresh токеном.

    :param response: Ответ на запрос;
    :param settings: Настройки cookie;
    :param refresh_token: Refresh токен;
    :param expires_in: Время жизни токена;
    :return: None
    """
    response.set_cookie(
        key=settings.refresh_token_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_same_site,
        max_age=expires_in
    )


def set_auth_cookies(
        response: Response,
        settings: AuthCookieSettings,
        access_token: str,
        access_expires: int | None,
        refresh_token: str,
        refresh_expires: int | None
) -> None:
    """
    Установка cookie с токенами авторизации.

    :param response: Response - объект ответа FastAPI;
    :param settings: Настройки cookie.
    :param access_token: access токен;
    :param refresh_token: refresh токен;
    :param access_expires: время жизни access токена;
    :param refresh_expires: время жизни refresh токена.
    :returns: None.
    """
    set_access_token_cookie(
        response,
        settings,
        access_token,
        access_expires
    )
    set_refresh_token_cookie(
        response,
        settings,
        refresh_token,
        refresh_expires
    )


def set_user_cookie(
        response: Response,
        settings: CookieSettings,
        user_data: UserPublic,
        access_expires: int | None
) -> None:
    """
    Установка cookie с данными пользователя. Cookie устанавливаются на время
    жизни access токена.

    :param response: Response - объект ответа FastAPI.
    :param settings: Настройки cookie.
    :param user_data: Данные пользователя.
    :param access_expires: Время жизни токена.
    :return: None
    """
    response.set_cookie(
        key=settings.user_email_cookie_name,
        value=user_data.email,
        max_age=access_expires
    )
    response.set_cookie(
        key=settings.user_role_cookie_name,
        value=user_data.role,
        max_age=access_expires
    )
    response.set_cookie(
        key=settings.user_id_cookie_name,
        value=str(user_data.id),
        max_age=access_expires
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


class AuthCookieMiddleware(BaseHTTPMiddleware):
    """Middleware для автоматической подстановки токенов из cookie"""
    __PASS_ENDPONTS = (
        "/",
        "/health",
        "/auth/login",
        "/auth/register",
        "/favicon.ico"
    )

    async def dispatch(self, request: Request, call_next):
        settings: Settings = request.app.state.settings

        if self._should_skip_auth(request, settings):
            return await call_next(request)

        try:
            access_token, new_access_token = await self._get_or_refresh_token(
                request, settings)
            self._set_auth_state(request, settings.cookie, access_token)
            response = await call_next(request)
        except NotAuthenticated:
            return LOGIN_REDIRECT
        if new_access_token:
            set_access_token_cookie(
                response,
                settings.auth_cookie,
                new_access_token.access_token,
                new_access_token.expires_in
            )
        return response

    def _should_skip_auth(self, request: Request, settings: Settings) -> bool:
        """
        Проверка, что запрос не требует аутентификации.

        :param request: Запрос пользователя.
        :param settings: Настройки приложения.
        :return: True, если запрос не требует аутентификации, иначе False.
        """
        return (
                request.url.path.startswith(settings.jinja.static_url) or
                request.url.path in self.__PASS_ENDPONTS
        )

    async def _get_or_refresh_token(
            self,
            request: Request,
            settings: Settings
    ) -> tuple[str | None, RefreshTokenResponse | None]:
        """
        Получение или обновление токена авторизации.

        :param request: Запрос пользователя.
        :param settings: Настройки приложения.
        :return: Access токен, данные о новом access токене (если обновлен).
        """
        access_token = request.cookies.get(
            settings.auth_cookie.access_token_cookie_name
        )

        if access_token:
            return access_token, None

        refresh_token = request.cookies.get(
            settings.auth_cookie.refresh_token_cookie_name
        )

        if not refresh_token:
            raise NotAuthenticated("Пользователь не авторизован")

        return await self._refresh_access_token(refresh_token, settings)

    @staticmethod
    async def _refresh_access_token(
            refresh_token: str,
            settings: Settings
    ) -> tuple[str, RefreshTokenResponse]:
        """
        Обновление access токена по refresh токену.

        :param refresh_token: Refresh токен.
        :param settings: Настройки приложения.

        :return: Access токен и данные о новом access токене.
        """
        auth_client = AuthClient(
            settings.auth_service.url,
            settings.auth_service.timeout,
            settings.auth_header_name
        )
        try:
            new_access_token: RefreshTokenResponse = \
                await auth_client.refresh_token(refresh_token)
            return new_access_token.access_token, new_access_token
        except Exception as err:
            logger.error(
                f"Ошибка обновления токена: {err} "
                f"({err.__class__.__name__})"
            )
            raise NotAuthenticated("Не удалось обновить access токен")

    @staticmethod
    def _set_auth_state(
            request: Request,
            cookie_settings: CookieSettings,
            access_token: str
    ) -> None:
        """
        Установка состояния аутентификации пользователя.

        :param request: Запрос пользователя.
        :param cookie_settings: Настройки cookie.
        :param access_token: Access токен.
        :return: None.
        """
        user_id: str = request.cookies.get(cookie_settings.user_id_cookie_name)
        email: str = request.cookies.get(
            cookie_settings.user_email_cookie_name
        )
        role: str = request.cookies.get(cookie_settings.user_role_cookie_name)

        user = User(id=user_id, email=email, role=role)
        request.state.user = user
        request.state.access_token = access_token
        request.state.is_authenticated = True
