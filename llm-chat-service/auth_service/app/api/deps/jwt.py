from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from loguru import logger

from auth_service.app.consts.jwt_token import TokenDataKeys
from auth_service.app.core.exceptions.jwt_token import VerifyTokenError
from auth_service.app.core.security.jwt_token import verify_access_token
from auth_service.app.schemas.token_data import AccessTokenData
from auth_service.app.schemas.user import TokenUserData
from auth_service.app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _get_user_data(token: str) -> TokenUserData:
    """
    Получение данных пользователя из JWT токена.

    :param token: JWT токен.
    :return: Данные пользователя.

    :raises HTTPException: Если токен невалидный.
    """
    try:
        payload: AccessTokenData = verify_access_token(
            token,
            settings.jwt.access_secret.secret,
            settings.jwt.alg
        )
        user_data = TokenUserData(
            user_id=int(payload.sub),
            user_role=payload.role
        )
    except ValueError as err:
        err_title = "Невалидный токен"
        logger.error(f"{err_title}: {err} ({err.__class__.__name__})")
        raise VerifyTokenError(err_title)
    return user_data


def get_current_user_id(
        token: Annotated[str, Depends(oauth2_scheme)]
) -> int:
    """
    Получение ID текущего пользователя из JWT токена.

    :param token: JWT токен.

    :return: ID пользователя

    :raises HTTPException: Если токен невалидный.
    """
    user_data = _get_user_data(token)
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
    return _get_user_data(token)


UserIdDep = Annotated[int, Depends(get_current_user_id)]
UserDataDep = Annotated[TokenUserData, Depends(get_current_user)]
