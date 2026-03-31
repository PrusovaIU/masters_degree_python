from datetime import timedelta
from typing import Any

import jwt

from .token_data import TokenData, AccessTokenData, RefreshTokenData
from loguru import logger
from auth_service.app.core.exceptions import jwt_token as token_errors


def _encode_token(data: TokenData, secret: str, alg: str) -> str:
    """
    Кодирование JWT токена.

    :param data: Данные токена.
    :param secret: Ключ для подписи.
    :param alg: Алгоритм подписи.
    :return: JWT токен.

    :raises TokenEncodeError: Если токен не может быть создан.
    """
    try:
        token = jwt.encode(
            data.model_dump(),
            key=secret,
            algorithm=alg
        )
        logger.debug(
            f"Создан access токен для sub={data.sub}, role={data.role}"
        )
    except Exception as err:
        logger.error(
            f"Ошибка кодирования JWT для sub={data.sub}, role={data.role}: "
            f"{err}"
        )
        raise token_errors.TokenEncodeError(
            "Не удалось создать JWT токен"
        ) from err
    return token


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
    data = AccessTokenData.new(subject, role, expires_delta, payload)
    return _encode_token(data, secret, alg)


def create_refresh_token(
        subject: str | int,
        expires_delta: timedelta,
        secret: str,
        alg: str,
) -> str:
    """
    Создание подписанного JWT refresh токена.

    :param subject: Идентификатор пользователя.
    :param expires_delta: Время жизни токена.
    :param secret: Ключ для подписи.
    :param alg: Алгоритм подписи.

    :return: JWT токен.

    :raises TokenEncodeError: Если токен не может быть создан.
    """
    data = RefreshTokenData.new(subject, expires_delta)
    return _encode_token(data, secret, alg)

