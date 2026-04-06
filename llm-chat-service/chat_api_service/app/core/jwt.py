from chat_api_service.app.schemas.token import AccessTokenData
from chat_api_service.app.core.exceptions import jwt_token as excs
import jwt
from loguru import logger


def decode_and_validate(
        token: str,
        secret: str,
        alg: str
) -> AccessTokenData:
    """
    Декодирование и валидация JWT access токена.

    :param token: JWT access токен.
    :param secret: Секретный ключ для декодирования токена.
    :param alg: Алгоритм шифрования токена.
    :return: Декодированные данные токена.

    :raises jwt_token.JWTTokenInvalid: Если токен недействителен.
    :raises jwt_token.JWTTokenExpired: Если истек срок жизни токена.
    :raises jwt_token.JWTTokenException: Если не удалось декодировать токен.
    """
    try:
        payload = jwt.decode(
            token,
            key=secret,
            algorithms=[alg]
        )
    except jwt.ExpiredSignatureError:
        err_msg = "Истек срок жизни токена"
        logger.warning(err_msg)
        raise excs.JWTTokenExpired(err_msg)
    except jwt.InvalidTokenError as exc:
        logger.warning(
            f"Ошибка декодирования токена: {exc} ({exc.__class__.__name__})"
        )
        raise excs.JWTTokenInvalid("Недействительный токен")
    except Exception as exc:
        logger.error(
            f"Не удалось декодировать токен: {exc} ({exc.__class__.__name__})"
        )
        raise excs.JWTTokenException("Ошибка декодирования токена")
    return AccessTokenData(**payload)
