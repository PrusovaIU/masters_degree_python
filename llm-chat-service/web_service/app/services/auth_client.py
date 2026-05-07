from httpx import HTTPStatusError, Response, TimeoutException
from loguru import logger
from starlette import status

from libs.schemas.auth import (LoginResponse, RefreshTokenRequest,
                               RefreshTokenResponse, RegisterRequest,
                               RegisterResponse)
from libs.schemas.user import UserPublic
from web_service.app.core.exceptions import auth_client as errs
from web_service.app.core.utils.httpx_client import (BaseClient,
                                                     error_handler_decorator)


class AuthClient(BaseClient):
    """
    Клиент для взаимодействия с auth_service.
    """
    async def register(
            self,
            data: RegisterRequest
    ) -> RegisterResponse:
        """
        Регистрация нового пользователя

        :param data: Данные для регистрации.
        :return: Ответ сервиса авторизации.

        :raises RegisterError: Ошибка регистрации.
        :raises UserAlreadyExistsError: Пользователь уже существует.
        """
        title_err = f"Ошибка регистрации пользователя \"{data.email}\""
        try:
            async with self._get_client() as client:
                resp: Response = await client.post(
                    "/auth/register",
                    json=data.model_dump()
                )
                resp.raise_for_status()
                return RegisterResponse(**resp.json())
        except HTTPStatusError:
            if resp.status_code == status.HTTP_409_CONFLICT:
                raise errs.UserAlreadyExistsError(
                    "Пользователь уже существует", data.email
                )
            logger.error(
                f"{title_err}: {resp.text} (status={resp.status_code})"
            )
            raise errs.RegisterError(
                f"{resp.text} (status={resp.status_code})",
                str(data.email)
            )
        except TimeoutException:
            logger.error(f"{title_err}: timeout error")
            raise errs.RegisterError(
                "timeout error", str(data.email)
            )
        except Exception as err:
            logger.error(f"{title_err}: {err} ({err.__class__.__name__})")
            raise errs.RegisterError(
                "Ошибка регистрации", str(data.email)
            )

    async def login(
            self,
            username: str,
            password: str
    ) -> LoginResponse:
        """
        Авторизация пользователя.

        :param username: Имя пользователя.
        :param password: Пароль пользователя.

        :return: Ответ сервиса авторизации.

        :raises LoginError: Ошибка авторизации.
        """
        title_err = f"Ошибка авторизации пользователя: {username}"
        try:
            async with self._get_client() as client:
                form_data = {
                    "grant_type": "password",
                    "username": username,
                    "password": password,
                    "scope": "",
                }
                resp: Response = await client.post(
                    "/auth/login",
                    data=form_data
                )
                resp.raise_for_status()
                return LoginResponse(**resp.json())
        except HTTPStatusError:
            logger.error(
                f"{title_err}: {resp.text} (status={resp.status_code})"
            )
            raise errs.LoginError(
                f"{resp.text} (status={resp.status_code})",
                str(username)
            )
        except TimeoutException:
            logger.error(f"{title_err}: timeout error")
            raise errs.LoginError("timeout error", str(username))
        except Exception as err:
            logger.error(f"{title_err}: {err} ({err.__class__.__name__})")
            raise errs.LoginError(
                "Ошибка авторизации",
                str(username)
            )

    @error_handler_decorator(
        errs.RefreshTokenError,
        "Ошибка обновления токена"
    )
    async def refresh_token(
            self,
            refresh_token: str
    ) -> RefreshTokenResponse:
        """
        Обновление access токена по refresh токену.

        :param refresh_token: Refresh токен.
        :return: Ответ сервиса авторизации.

        :raises RefreshTokenError: Ошибка обновления токена.
        """
        data = RefreshTokenRequest(
            refresh_token=refresh_token
        ).model_dump()
        async with self._get_client() as client:
            resp = await client.post(
                "/auth/refresh",
                json=data
            )
            resp.raise_for_status()
        return RefreshTokenResponse(**resp.json())

    @error_handler_decorator(
        errs.ProfileError,
        "Ошибка получения профиля"
    )
    async def get_me(self, access_token: str) -> UserPublic:
        """
        Получение профиля текущего пользователя.

        :param access_token: Access токен.

        :return: Профиль пользователя.

        :raises ProfileError: Ошибка получения профиля.
        """
        async with self._get_client(access_token) as client:
            resp = await client.get("/auth/me")
            resp.raise_for_status()
            return UserPublic(**resp.json())
