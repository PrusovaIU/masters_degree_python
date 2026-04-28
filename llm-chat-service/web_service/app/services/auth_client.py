from collections.abc import AsyncGenerator

from httpx import AsyncClient, HTTPStatusError, Timeout, TimeoutException, \
    Response
from typing import Optional

from web_service.app.core.config import settings
from libs.schemas.auth import (
    RegisterRequest, RegisterResponse, LoginResponse,
    RefreshTokenRequest, RefreshTokenResponse
)
from libs.schemas.user import UserPublic
from web_service.app.core.exceptions import auth_client as errs
from loguru import logger



class AuthClient:
    """
    HTTP-клиент для взаимодействия с auth_service.

    :param url: URL auth_service.
    :param timeout: Таймаут запроса.
    :param auth_token_name: Имя заголовка с токеном авторизации.
    """

    def __init__(self, url: str, timeout: float, auth_token_name: str):
        self._base_url = url
        self._timeout = Timeout(timeout)
        self._auth_token_name = auth_token_name

    async def _get_client(
            self,
            access_token: str  | None = None
    ) -> AsyncGenerator[AsyncClient, None]:
        """
        Получение HTTP-клиента.

        :param access_token: Access токен. Если None, то запрос не авторизован.
        :return: HTTP-клиент.
        """
        async with AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout
        ) as client:
            if access_token:
                header = f"Bearer {access_token}"
                client.headers[self._auth_token_name] = header
            yield client

    async def register(
            self,
            data: RegisterRequest
    ) -> RegisterResponse:
        """
        Регистрация нового пользователя

        :param data: Данные для регистрации.
        :return: Ответ сервиса авторизации.

        :raises RegisterError: Ошибка регистрации.
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
                f"timeout error", str(data.email)
            )
        except Exception as err:
            logger.error( f"{title_err}: {err} ({err.__class__.__name__})")
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
            raise errs.LoginError(f"timeout error", str(username))
        except Exception as err:
            logger.error(f"{title_err}: {err} ({err.__class__.__name__})")
            raise errs.LoginError(
                "Ошибка авторизации",
                str(username)
            )

    async def refresh_token(
            self,
            refresh_token: str
    ) -> RefreshTokenResponse | None:
        """
        Обновление access токена по refresh токену.

        :param refresh_token: Refresh токен.
        :return: Ответ сервиса авторизации.

        :raises RefreshTokenError: Ошибка обновления токена.
        """
        try:
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
        except HTTPStatusError:
            logger.error(
                f"Ошибка обновления токена: {resp.text} "
                f"(status={resp.status_code})"
            )
            raise errs.RefreshTokenError(
                f"{resp.text} (status={resp.status_code})"
            )
        except TimeoutException:
            logger.error(f"Ошибка обновления токена: timeout error")
            raise errs.RefreshTokenError("timeout error")
        except Exception as err:
            logger.error(
                f"Ошибка обновления токена: {err} ({err.__class__.__name__})"
            )
            raise errs.RefreshTokenError("Ошибка обновления токена")

    async def get_me(self, access_token: str) -> UserPublic | None:
        """
        Получение профиля текущего пользователя.

        :param access_token: Access токен.

        :return: Профиль пользователя.

        :raises ProfileError: Ошибка получения профиля.
        """
        title_err = "Ошибка получения профиля пользователя"
        try:
            async with self._get_client(access_token) as client:
                resp = await client.get("/auth/me")
                resp.raise_for_status()
                return UserPublic(**resp.json())
        except HTTPStatusError:
            logger.error(
                f"{title_err}: {resp.text} (status={resp.status_code})"
            )
            raise errs.ProfileError(f"{resp.text} (status={resp.status_code})")
        except TimeoutException:
            logger.error(f"{title_err}: timeout error")
            raise errs.ProfileError(f"timeout error")
        except Exception as err:
            logger.error(f"{title_err}: {err} ({err.__class__.__name__})")
            raise errs.ProfileError(title_err)
