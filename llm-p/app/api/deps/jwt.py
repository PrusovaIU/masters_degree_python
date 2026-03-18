from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jose import jwt
from app.core.config import settings
from app.core.errors.jwt import TokenVerifyError
from app.consts.jwt_token import TokenDataKeys
from loguru import logger


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

_AUTH_HEADERS = {"WWW-Authenticate": "Bearer"}


async def get_current_user_id(
        token: Annotated[str, Depends(oauth2_scheme)]
) -> int:
    """
    Получение ID текущего пользователя из JWT токена.

    :param token: JWT токен.

    :return: ID пользователя

    :raises HTTPException: Если токен невалидный.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt.secret,
            algorithms=[settings.jwt.algorithm]
        )
        user_id: str = payload[TokenDataKeys.SUB]
    except TokenVerifyError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=err.message,
            headers=_AUTH_HEADERS
        )
    except KeyError as err:
        logger.error(
            f"Cannot get user ID from token: "
            f"there is no {err} key in token data"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers=_AUTH_HEADERS
        )
    return int(user_id)
