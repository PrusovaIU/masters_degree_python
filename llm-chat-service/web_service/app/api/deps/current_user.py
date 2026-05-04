from fastapi import Request, Depends
from typing import Annotated


def get_access_token(request: Request) -> str | None:
    """
    Получение access токена текущего пользователя.

    :param request: Запрос пользователя.

    :return: Access токен текущего пользователя или None,
        если пользователь не авторизован.
    """
    if not getattr(request.state, "is_authenticated", False):
        return None
    return request.state.access_token


AccessTokenDep = Annotated[str | None, Depends(get_access_token)]
