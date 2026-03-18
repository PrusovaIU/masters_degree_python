from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt, JWTError, ExpiredSignatureError

from app.consts.jwt_token import TokenDataKeys
from app.core.config import settings
from loguru import logger

from app.core.errors.jwt import TokenVerifyError, TokenExpiredError, CreateTokenError

# Unix epoch time
_UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _total_seconds(dt: datetime) -> int:
    """
    :param dt: datetime
    :return: количество секунд с 01.01.1970.
    """
    total = (dt - _UNIX_EPOCH).total_seconds()
    return int(total)


def _calc_expire(expires_delta: timedelta | None) -> datetime:
    """
    Вычисление времени жизни токена.

    :param expires_delta: Время жизни токена. Если None,
        используется значение из конфигурации.

    :return: token expire.
    """
    if not expires_delta:
        expires_delta = settings.jwt.access_token_expires
    return datetime.now(timezone.utc) + expires_delta


def _form_token_data(
        user_id: int,
        role: str,
        expires_delta: timedelta | None = None,
        payload: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Формирование данных токена.

    :param user_id: Идентификатор пользователя.

    :param role: Роль пользователя.

    :param expires_delta: Время жизни токена. Если None,
        используется значение из конфигурации.

    :param payload: Дополнительные данные для токена.

    :return: Данные токена.
    """
    expire = _calc_expire(expires_delta)
    token_data = {
        TokenDataKeys.SUB: str(user_id),
        TokenDataKeys.ROLE: role,
        TokenDataKeys.EXP: _total_seconds(expire),
        TokenDataKeys.IAT: _total_seconds(datetime.now(timezone.utc))
    }
    if payload:
        token_data.update(payload)
    return token_data


def create_access_token(
        user_id: int,
        role: str,
        expires_delta: timedelta | None = None,
        payload: dict[str, Any] | None = None
) -> str:
    """
    Создание access токена.

    :param user_id: Идентификатор пользователя.

    :param role: Роль пользователя.

    :param expires_delta: Время жизни токена. Если None,
        используется значение из конфигурации.

    :param payload: Дополнительные данные для токена.

    :return: JWT токен.

    :raises app.core.errors.jwt.CreateTokenError: Если не удалось создать
        токен.
    """
    token_data = _form_token_data(user_id, role, expires_delta, payload)
    try:
        token: str = jwt.encode(
            token_data,
            settings.jwt.secret,
            algorithm=settings.jwt.alg
        )
    except JWTError as err:
        logger.error(f"Create token error: {err} ({err.__class__.__name__})")
        raise CreateTokenError("Create token error") from err
    return token


def verify_access_token(token: str) -> dict[str, Any]:
    """
    Валидация access токена.

    :param token: JWT токен для декодирования.

    :return: Payload токена если токен валиден.

    :raises app.core.errors.jwt.TokenVerifyError: Если токен не валиден.
    """
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.jwt.secret,
            algorithms=[settings.jwt.alg]
        )
    except ExpiredSignatureError as err:
        logger.error("Token expired")
        raise TokenExpiredError("Token expired") from err
    except JWTError as err:
        logger.error(f"Verify token error: {err}")
        raise TokenVerifyError("Invalid token") from err
    return payload
