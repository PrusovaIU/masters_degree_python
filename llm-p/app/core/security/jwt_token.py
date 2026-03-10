from datetime import datetime, timedelta, timezone
from typing import Optional, Any

from jose import jwt, JWTError

from app.core.config import SETTINGS
from enum import Enum
from loguru import logger


class TokenDataKeys(str, Enum):
    SUB = "sub"
    ROLE = "role"
    EXP = "exp"
    IAT = "iat"


class TokenError(Exception):
    """Ошибка работы с токеном"""
    pass


class TokenVerifyError(TokenError):
    """Ошибка верификации токена"""
    pass


def create_access_token(
        user_id: str,
        role: str,
        expires_delta: Optional[timedelta] = None,
        payload: Optional[dict[str, Any]] = None
) -> str:
    """
    Создание access токена.

    :param user_id: Идентификатор пользователя.

    :param role: Роль пользователя.

    :param expires_delta: Время жизни токена. Если None,
        используется значение из конфигурации.

    :param payload: Дополнительные данные для токена.

    :return: JWT токен.
    """
    expire: datetime = datetime.now(timezone.utc) + expires_delta \
        if expires_delta \
        else SETTINGS.jwt.access_token_expires

    token_data = {
        TokenDataKeys.SUB.value: str(user_id),
        TokenDataKeys.ROLE.value: role,
        TokenDataKeys.EXP.value: int(expire.timestamp()),
        TokenDataKeys.IAT.value: int(datetime.now(timezone.utc).timestamp())
    }

    if payload:
        token_data.update(payload)

    return jwt.encode(
        token_data,
        SETTINGS.jwt.secret,
        algorithm=SETTINGS.jwt.algorithm
    )


def verify_access_token(token: str) -> dict[str, Any]:
    """
    Валидация access токена.

    :param token: JWT токен для декодирования.

    :return: Payload токена если токен валиден.

    :raises TokenVerifyError: Если токен не валиден.
    """
    try:
        payload = jwt.decode(
            token,
            SETTINGS.jwt.secret,
            algorithms=[SETTINGS.jwt.alg]
        )
        return payload
    except JWTError as err:
        logger.error(f"Verify token error: {err}")
        raise TokenVerifyError("Invalid token")
