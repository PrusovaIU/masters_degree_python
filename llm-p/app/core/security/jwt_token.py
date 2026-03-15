from datetime import datetime, timedelta, timezone
from typing import Optional, Any

from jose import jwt, JWTError, ExpiredSignatureError

from app.core.config import settings
from enum import Enum
from loguru import logger


 # Unix epoch time
_UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


class TokenDataKeys(str, Enum):
    """Ключи данных в токене"""
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


def _total_seconds(dt: datetime) -> int:
    """
    :param dt: datetime
    :return: количество секунд с 01.01.1970.
    """
    total = (dt - _UNIX_EPOCH).total_seconds()
    return int(total)


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
    if not expires_delta:
        expires_delta = settings.jwt.access_token_expires

    expire: datetime = datetime.now(timezone.utc) + expires_delta

    token_data = {
        TokenDataKeys.SUB.value: str(user_id),
        TokenDataKeys.ROLE.value: role,
        TokenDataKeys.EXP.value: _total_seconds(expire),
        TokenDataKeys.IAT.value: _total_seconds(datetime.now(timezone.utc))
    }

    if payload:
        token_data.update(payload)

    return jwt.encode(
        token_data,
        settings.jwt.secret,
        algorithm=settings.jwt.alg
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
            settings.jwt.secret,
            algorithms=[settings.jwt.alg]
        )
        return payload

    except ExpiredSignatureError:
        logger.error("Token expired")
        raise TokenVerifyError("Token expired")
    except JWTError as err:
        logger.error(f"Verify token error: {err}")
        raise TokenVerifyError("Invalid token")
