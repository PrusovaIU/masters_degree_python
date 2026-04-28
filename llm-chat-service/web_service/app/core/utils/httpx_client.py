from collections.abc import AsyncGenerator
from functools import wraps
from typing import Type
from httpx import AsyncClient, HTTPStatusError, Timeout, TimeoutException
from loguru import logger
from web_service.app.core.exceptions.base import AppException


def error_handler_decorator(err_type: Type[AppException], title: str):
    """
    Декоратор для обработки ошибок, возникающих в httpx клиенте.

    :param err_type: Тип пробрасываемого исключения.
    :param title: Заголовок ошибки.
    :return:
    """
    async def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPStatusError as err:
                logger.error(
                    f"{title}: status error "
                    f"({err.response.status_code} - {err.response.text})"
                )
                raise err_type(
                    f"{err.response.status_code} ({err.response.text})"
                )
            except TimeoutException:
                logger.error(f"{title}: timeout error")
                raise err_type("timeout error")
            except Exception as err:
                logger.error(f"{title}: {err} ({err.__class__.__name__})")
                raise err_type(title)
        return wrapper
    return decorator


class BaseClient:
    """
    Базовый клиент для работы с HTTP API.

    :param url: URL сервиса.
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
