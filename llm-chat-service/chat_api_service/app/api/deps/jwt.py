from typing import Annotated

from fastapi import Request, Depends, HTTPException, status, Header
from libs.jwt_token.get_current_user import get_user_data
from chat_api_service.app.core.config import settings
from libs.jwt_token.token_data import TokenUserData


# def _get_token_from_header(request: Request) -> str:
#     """
#     Получение токена из заголовка.
#
#     :param request: Запрос.
#     :return: JWT токен.
#     """
#     token: str = request.headers.get(settings.jwt.header_name)
#     if token is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Not authenticated"
#         )
#     return token


JWTTokenHeader = Annotated[str, Header(alias=settings.jwt.header_name)]


def get_current_user_id(token: JWTTokenHeader) -> int:
    """
    Получение ID текущего пользователя из JWT токена.

    :param token: JWT токен.

    :return: ID пользователя

    :raises HTTPException: Если токен невалидный, или отсутствует авторизация.
    """
    user_data = get_user_data(
        token,
        settings.jwt.access_secret.secret,
        settings.jwt.alg
    )
    return user_data.user_id


def get_current_user(token: JWTTokenHeader) -> TokenUserData:
    """
    Получение данных текущего пользователя из JWT токена.

    :param token: JWT токен.
    :return: Данные пользователя.

    :raises HTTPException: Если токен невалидный, или отсутствует авторизация.
    """
    return get_user_data(
        token,
        settings.jwt.access_secret.secret,
        settings.jwt.alg
    )


UserIdDep = Annotated[int, Depends(get_current_user_id)]
UserDataDep = Annotated[TokenUserData, Depends(get_current_user)]
