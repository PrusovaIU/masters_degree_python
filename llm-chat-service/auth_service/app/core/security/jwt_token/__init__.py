from datetime import timedelta
from typing import Any

import jwt

from auth_service.app.consts.token_type import TokenType
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
    data = AccessTokenData.new(subject, role, expires_delta, payload)
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
    data = RefreshTokenData.new(subject, expires_delta)
    return _encode_token(data, secret, alg)


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

    :raises TokenDecodeError: Если токен не может быть декодирован.
    """
    options = {
        "verify_signature": True,
        "verify_exp": verify_exp,
        "verify_iat": True,
        "require": ["exp", "iat", "sub"]
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
        raise token_errors.TokenDecodeError(err_msg) from err
    except jwt.InvalidSignatureError as err:
        logger.warning("Неверная подпись JWT токена")
        raise tokTokenDecodeError("Неверная подпись токена") from err
    except jwt.InvalidTokenError as err:
        logger.warning(f"Невалидный JWT токен: {err}")
        raise TokenDecodeError(f"Невалидный токен: {err}",
                               token_error=err) from err
    except Exception as err:
        logger.error(f"Непредвиденная ошибка при декодировании токена: {err}")
        raise TokenDecodeError("Ошибка при декодировании токена",
                               token_error=err) from err


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


def decode_token(
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
    try:
        payload = _decode_token(token, secret, alg, verify_exp)
        _check_token_type(payload, expected_type)
        try:
        except KeyError as err:
            logger.error(
                f"Неверный формат JWT токена: параметр {err} отсутствует"
            )
            raise token_errors.TokenDecodeError("Неверный формат JWT токена")

        # Конвертируем timestamp в datetime для удобства
        exp_dt = None
        iat_dt = None
        if "exp" in payload:
            exp_dt = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        if "iat" in payload:
            iat_dt = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)

        # Извлекаем дополнительные данные
        extra = {k: v for k, v in payload.items()
                 if k not in ["sub", "role", "type", "exp", "iat"]}

        return TokenData(
            sub=str(payload["sub"]),
            role=payload.get("role"),
            token_type=token_type,
            exp=exp_dt,
            iat=iat_dt,
            extra=extra,
        )



