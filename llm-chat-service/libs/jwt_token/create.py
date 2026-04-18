from datetime import timedelta
from typing import Any

import jwt
from loguru import logger

from libs.jwt_token import exceptions as token_errors
from libs.jwt_token.token_data import TokenData, AccessTokenData, \
    RefreshTokenData


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
        logger.debug(f"Создан access токен для sub={data.sub}")
    except Exception as err:
        logger.error(f"Ошибка кодирования JWT для sub={data.sub}: {err}")
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
        payload: dict[str, Any] | None  = None
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
    data = AccessTokenData.new(str(subject), expires_delta, role, payload)
    return _encode_token(data, secret, alg)


def create_refresh_token(
        subject: str | int,
        expires_delta: timedelta,
        secret: str,
        alg: str
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
    data = RefreshTokenData.new(str(subject), expires_delta)
    return _encode_token(data, secret, alg)
