from starlette.responses import RedirectResponse

from libs.schemas.user import UserPublic
from web_service.app.schemas.config import Settings
from web_service.app.services.auth_client import AuthClient
from fastapi import Request
from web_service.app.services.auth_client import AuthClient
from libs.schemas.auth import (
    RegisterRequest, RegisterResponse, LoginResponse,
    RefreshTokenRequest, RefreshTokenResponse
)
from web_service.app.core.exceptions import auth_client as errors


class AuthUsecase:
    """
    Usecase для авторизации.

    :param auth_client: Клиент для работы с сервисом авторизации.
    :params settings: Настройки приложения.
    """
    def __init__(
            self,
            auth_client: AuthClient,
            settings: Settings
    ) -> None:
        self._auth_client = auth_client
        self._settings = settings

    @staticmethod
    async def auth_page(request: Request) -> UserPublic | None:
        if not getattr(request.state, "is_authenticated", False):
            return None
        access_token = request.state.access_token
        try:
            resp: UserPublic = await AuthClient.get_me(access_token)
        except Exception:
            return None
        return resp

    async def auth(self, username: str, password: str) -> LoginResponse:
        """
        Авторизация пользователя.

        :param username: Имя пользователя.
        :param password: Пароль пользователя.
        :return: Ответ от сервиса авторизации.
        """
        return await self._auth_client.login(username, password)
