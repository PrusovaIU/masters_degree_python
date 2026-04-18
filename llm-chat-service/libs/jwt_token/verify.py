from typing import Any, TypeVar

import jwt
from loguru import logger

from libs.jwt_token.consts import TokenType
from libs.jwt_token import exceptions as token_errors
from libs.jwt_token.token_data import TokenData, AccessTokenData, RefreshTokenData


TokenDataT = TypeVar('TokenDataT', bound=TokenData, covariant=True)


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
    :raises InvalidTokenError: Если токен не прошел валидацию.
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
        logger.warning(f"{err_msg}: {err} ({err.__class__.__name__})")
        raise token_errors.InvalidTokenError(err_msg) from err
    except Exception as err:
        err_msg = "Ошибка при декодировании JWT токена"
        logger.error(f"{err_msg}: {err} ({err.__class__.__name__})")
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

    :raises InvalidTokenError: Если тип токена не совпадает с ожидаемым.
    """
    token_type = payload.get("type")
    if token_type != expected_type:
        err_msg = f"ожидался '{expected_type}', получен '{token_type}'"
        logger.error(f"Неверный тип токена: {err_msg}")
        raise token_errors.InvalidTokenError(err_msg)


def verify_token(
        token: str,
        expected_type: TokenType,
        secret: str,
        alg: str,
        verify_exp: bool = True
) -> TokenDataT:
    """
    Декодирует и валидирует JWT токен.

    :param token: JWT токен в виде строки.
    :param secret: Ключ для проверки подписи.
    :param alg: Алгоритм подписи.
    :param expected_type: Ожидаемый тип токена.
    :param verify_exp: Проверять ли срок действия токена.

    :return: Декодированные данные токена.

    :raises TokenExpiredError: Если срок действия токена истек.
    :raises InvalidTokenError: Если токен не прошел валидацию.
    :raises TokenDecodeError: Если токен не может быть декодирован.
    """
    payload = _decode_token(token, secret, alg, verify_exp)
    _check_token_type(payload, expected_type)
    return TokenData.from_token_data(expected_type, **payload)


def verify_access_token(
        token: str,
        secret: str,
        alg: str,
        verify_exp: bool = True
) -> AccessTokenData:
    """
    Валидация и декодирование access токена.

    :param token: JWT токен в виде строки.
    :param secret: Ключ для проверки подписи.
    :param alg: Алгоритм подписи.
    :param verify_exp: Проверять ли срок действия токена.

    :raises TokenExpiredError: Если срок действия токена истек.
    :raises InvalidTokenError: Если токен не прошел валидацию.
    :raises TokenDecodeError: Если токен не может быть декодирован.
    """
    return verify_token(
        token,
        TokenType.access,
        secret,
        alg,
        verify_exp
    )


def verify_refresh_token(
        token: str,
        secret: str,
        alg: str,
        verify_exp: bool = True
) -> RefreshTokenData:
    """
    Валидация и декодирование refresh токена.

    :param token: JWT токен в виде строки.
    :param secret: Ключ для проверки подписи.
    :param alg: Алгоритм подписи.
    :param verify_exp: Проверять ли срок действия токена.

    :raises TokenExpiredError: Если срок действия токена истек.
    :raises InvalidTokenError: Если токен не прошел валидацию.
    :raises TokenDecodeError: Если токен не может быть декодирован.
    """
    return verify_token(
        token,
        TokenType.refresh,
        secret,
        alg,
        verify_exp
    )
