from typing import Any

import jwt
from loguru import logger

from auth_service.app.consts.token_type import TokenType
from auth_service.app.core.exceptions import jwt_token as token_errors
from auth_service.app.schemas.token_data import TokenData


def _decode_token(
        token: str,
        secret: str,
        alg: str,
        verify_exp: bool = True,
) -> dict[str, Any]:
    """
    Декодирование JWT токена.

    :param token: JWT токен.
    :param secret: Ключ для проверки подписи.
    :param alg: Алгоритм подписи.
    :param verify_exp: Проверять ли срок действия токена.
    :return: Декодированные данные токена.

    :raises TokenExpiredError: Если срок действия токена истек.
    :raises TokenDecodeError: Если токен не может быть декодирован.
    """
    options = {
        "verify_signature": True,
        "verify_exp": verify_exp,
        "verify_iat": True,
        "require": TokenData.model_params_vnames()
    }
    try:
        return jwt.decode(
            token,
            key=secret,
            algorithms=[alg],
            options=options
        )
    except jwt.ExpiredSignatureError as err:
        err_msg = "Срок действия токена истек"
        logger.warning(err_msg)
        raise token_errors.TokenExpiredError(err_msg) from err
    except jwt.PyJWTError as err:
        err_msg = "Невалидный JWT токен"
        logger.warning(err_msg)
        raise token_errors.TokenDecodeError(err_msg) from err


def _check_token_type(
        payload: dict[str, Any],
        expected_type: TokenType
) -> None:
    """
    Проверка типа токена.

    :param payload: Данные токена.
    :param expected_type: Ожидаемый тип токена.
    :return: None.

    :raises WrongTokenTypeError: Если тип токена не совпадает с ожидаемым.
    """
    token_type = payload.get("type")
    if token_type != expected_type:
        err_msg = f"ожидался '{expected_type}', получен '{token_type}'"
        logger.error(f"Неверный тип токена: {err_msg}")
        raise token_errors.InvalidTokenTypeError(err_msg)


def verify_token(
        token: str,
        expected_type: TokenType,
        secret: str,
        alg: str,
        verify_exp: bool = True,
) -> TokenData:
    """
    Декодирует и валидирует JWT токен.

    :param token: JWT токен в виде строки.
    :param secret: Ключ для проверки подписи.
    :param alg: Алгоритм подписи.
    :param expected_type: Ожидаемый тип токена.
    :param verify_exp: Проверять ли срок действия токена.

    :return: Декодированные данные токена.

    :raises TokenDecodeError: Если токен не может быть декодирован.
    """
    payload = _decode_token(token, secret, alg, verify_exp)
    _check_token_type(payload, expected_type)
    return TokenData.from_token_data(expected_type, **payload)
