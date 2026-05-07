from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from web_service.app.core.cookie import get_user_cookie
from web_service.app.schemas.config import Settings
from web_service.app.schemas.user import User


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


def get_admin_token(request: Request) -> str | None:
    """
    Проверка прав администратора.

    :param request: Запрос пользователя.
    :return: Access токен администратора.

    :raises HttpException: Если пользователь не является администратором.
    """
    if not getattr(request.state, "is_authenticated", False):
        return None
    settings: Settings = request.app.state.settings
    user_data: User = get_user_cookie(request, settings.cookie)
    if user_data.role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    return request.state.access_token


AccessTokenDep = Annotated[str | None, Depends(get_access_token)]
AdminTokenDep = Annotated[str | None, Depends(get_admin_token)]
