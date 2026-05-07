from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from web_service.app.services.auth_client import AuthClient
from libs.schemas.auth import RefreshTokenResponse
from loguru import logger

from .cookie import set_access_token_cookie, get_user_cookie
from .exceptions.security import NotAuthenticated

from web_service.app.schemas.config import Settings, CookieSettings
from web_service.app.api.login_redirect import LOGIN_REDIRECT
from web_service.app.schemas.user import User
from .exceptions.cookie import CookieUnfoundException
from .cookie import clear_auth_cookies


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
        except (NotAuthenticated, CookieUnfoundException):
            response = LOGIN_REDIRECT
            clear_auth_cookies(response, settings)
            return response
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
        return request.url.path in self.__PASS_ENDPONTS

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

        :raise CookieUnfoundException: если cookie не найдены.
        """
        user: User = get_user_cookie(request, cookie_settings)
        request.state.user = user
        request.state.access_token = access_token
        request.state.is_authenticated = True
