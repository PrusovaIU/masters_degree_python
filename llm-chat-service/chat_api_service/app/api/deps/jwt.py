from typing import Annotated

from fastapi import Depends, HTTPException, status
from chat_api_service.app.core.config import settings
from libs.jwt_token.token_data import TokenUserData


UserDataDep = Annotated[TokenUserData, Depends(settings.jwt.bearer)]


def get_admin(user: UserDataDep) -> TokenUserData:
    """
    Проверка доступа. Разрешен только админу.

    :param user: Текущий пользователь.
    :return: Данные пользователя.
    """
    if user.user_role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return user


AdminDep = Annotated[TokenUserData, Depends(get_admin)]
