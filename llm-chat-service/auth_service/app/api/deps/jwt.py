from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from auth_service.app.core.config import settings
from libs.jwt_token.get_current_user import get_user_data
from libs.jwt_token.token_data import TokenUserData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user_id(
        token: Annotated[str, Depends(oauth2_scheme)]
) -> int:
    """
    Получение ID текущего пользователя из JWT токена.

    :param token: JWT токен.

    :return: ID пользователя

    :raises HTTPException: Если токен невалидный.
    """
    user_data = get_user_data(
        token,
        settings.jwt.access_secret.secret,
        settings.jwt.alg
    )
    return user_data.user_id


def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)]
) -> TokenUserData:
    """
    Получение данных текущего пользователя из JWT токена.

    :param token: JWT токен.
    :return: Данные пользователя.

    :raises HTTPException: Если токен невалидный.
    """
    return get_user_data(
        token,
        settings.jwt.access_secret.secret,
        settings.jwt.alg
    )


UserIdDep = Annotated[int, Depends(get_current_user_id)]
UserDataDep = Annotated[TokenUserData, Depends(get_current_user)]
