from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from loguru import logger

from app.consts.jwt_token import TokenDataKeys
from app.core.errors.jwt import TokenVerifyError
from app.core.security.jwt_token import verify_access_token
from app.schemas.error_detail import Detail
from app.schemas.user import UserData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

AUTH_HEADERS = {"WWW-Authenticate": "Bearer"}


def _get_user_data(token: str) -> UserData:
    """
    Получение данных пользователя из JWT токена.

    :param token: JWT токен.
    :return: Данные пользователя.

    :raises HTTPException: Если токен невалидный.
    """
    try:
        payload = verify_access_token(token)
        user_data = UserData(
            user_id=int(payload[TokenDataKeys.SUB]),
            user_role=payload[TokenDataKeys.ROLE]
        )
    except TokenVerifyError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=err.detail.model_dump(),
            headers=AUTH_HEADERS
        )
    except KeyError as err:
        logger.error(
            f"Cannot get user ID from token: "
            f"there is no {err} key in token data"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=Detail(
                title="InvalidTokenError",
                message="Invalid token format"
            ),
            headers=AUTH_HEADERS
        )
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
) -> UserData:
    """
    Получение данных текущего пользователя из JWT токена.

    :param token: JWT токен.
    :return: Данные пользователя.

    :raises HTTPException: Если токен невалидный.
    """
    return _get_user_data(token)


UserIdDependency = Annotated[int, Depends(get_current_user_id)]
UserDataDependency = Annotated[UserData, Depends(get_current_user)]
