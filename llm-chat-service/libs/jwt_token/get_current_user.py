from loguru import logger

from libs.jwt_token.exceptions import VerifyTokenError
from libs.jwt_token import verify_access_token
from libs.jwt_token.token_data import AccessTokenData, TokenUserData


def get_user_data(token: str, secret: str, alg: str) -> TokenUserData:
    """
    Получение данных пользователя из JWT токена.

    :param token: JWT токен.
    :param secret: Секретный ключ.
    :param alg: Алгоритм подписи.
    :return: Данные пользователя.

    :raises HTTPException: Если токен невалидный.
    """
    try:
        payload: AccessTokenData = verify_access_token(
            token,
            secret,
            alg
        )
        user_data = TokenUserData(
            user_id=int(payload.sub),
            user_role=payload.role
        )
    except ValueError as err:
        err_title = "Невалидный токен"
        logger.error(f"{err_title}: {err} ({err.__class__.__name__})")
        raise VerifyTokenError(err_title)
    return user_data
