from libs.schemas.auth import (LoginResponse, RegisterRequest,
                               RegisterResponse)
from libs.schemas.user import UserPublic
from web_service.app.core.exceptions import auth_usecase as usecase_errors
from web_service.app.schemas.config import Settings
from web_service.app.services.auth_client import AuthClient


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

    async def get_user_data(self, access_token: str) -> UserPublic | None:
        """
        Получение данных пользователя.

        :param access_token: Токен доступа.

        :return: Данные пользователя, если пользователь авторизован,
            иначе None.
        """
        return await AuthClient.get_me(access_token)

    async def auth(self, username: str, password: str) -> LoginResponse:
        """
        Авторизация пользователя.

        :param username: Имя пользователя.
        :param password: Пароль пользователя.
        :return: Ответ от сервиса авторизации.
        """
        return await self._auth_client.login(username, password)

    async def register(
            self,
            username: str,
            password: str,
            password_confirm: str
    ) -> RegisterResponse:
        """
        Регистрация пользователя.

        :param username: Имя пользователя.
        :param password: Пароль пользователя.
        :param password_confirm: Подтверждение пароля.
        :return: Ответ от сервиса авторизации.
        """
        if password != password_confirm:
            raise usecase_errors.PasswordNotMatchException(
                "Пароли не совпадают"
            )
        return await self._auth_client.register(
            RegisterRequest(email=username, password=password)
        )

    async def me(self, access_token: str) -> UserPublic:
        """
        Получение данных пользователя.

        :param access_token: Access token.
        :return: Данные пользователя.
        """
        return await self._auth_client.get_me(access_token)
