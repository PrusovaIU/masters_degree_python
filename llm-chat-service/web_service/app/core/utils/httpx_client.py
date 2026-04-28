from functools import wraps
from typing import Type
from httpx import AsyncClient, HTTPStatusError, Timeout, TimeoutException, \
    Response
from loguru import logger
from web_service.app.core.exceptions.auth_client import AuthClientError


def error_handler_decorator(err_type: Type[AuthClientError], title: str):
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
                    f"{title}: auth_service вернул ошибку "
                    f"{err.response.status_code} ({err.response.text})"
                )
                raise err_type(
                    f"{err.response.status_code} ({err.response.text})}"
                )
