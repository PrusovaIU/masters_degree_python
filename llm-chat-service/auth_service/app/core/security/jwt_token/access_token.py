from datetime import timedelta, datetime, timezone
from typing import Any

import jwt

from auth_service.app.schemas.token_data import TokenData
from auth_service.app.consts.token_type import TokenType
from loguru import logger
from ...exceptions import jwt_token as token_errors


def create_access_token(
        subject: str | int,
        role: str,
        expires_delta: timedelta,
        secret: str,
        alg: str,
        payload: dict[str, Any] | None  = None,
) -> str:
    """
    Создание подписанного JWT access токен.

    :param subject: Идентификатор пользователя.
    :param role: Роль пользователя.
    :param expires_delta: Время жизни токена.
    :param secret: Секретный ключ для подписи.
    :param alg: Алгоритм подписи.
    :param payload: Дополнительные данные для токена.

    :return: JWT токен.

    :raises TokenEncodeError: Если токен не может быть создан.
    """
    try:
        now = datetime.now(timezone.utc)
        toke_data = TokenData(
            sub=str(subject),
            role=role,
            exp=now + expires_delta,
            iat=now,
            type=TokenType.access,
            payload=payload,
        )
        token = jwt.encode(
            toke_data.model_dump(),
            key=secret,
            algorithm=alg
        )
        logger.debug(f"Создан access токен для sub={subject}, role={role}")
    except Exception as err:
        logger.error(f"Ошибка кодирования JWT: {err}")
        raise token_errors.TokenEncodeError(
            "Не удалось создать JWT токен"
        ) from err
    return token
