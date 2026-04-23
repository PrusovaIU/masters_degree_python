from libs.jwt_token.get_current_user import get_user_data
from libs.jwt_token.token_data import TokenUserData
from fastapi.security import HTTPBearer
from fastapi import Request, HTTPException, status


class JWTBearer(HTTPBearer):
    """
    Bearer для валидации JWT токена.

    :param public_key: Секрет для проверки подписи токена.
    :param alg: Алгоритм подписи токена.
    :auth_header_name: Название заголовка с токеном.
    """
    def __init__(
            self,
            public_key: str,
            alg: str,
            auth_header_name: str,
    ):
        self._public_key = public_key
        self._alg = alg
        self._auth_header_name = auth_header_name

    async def __call__(self, request: Request) -> TokenUserData:
        """
        Проверка валидности токена.

        :param request: Запрос.
        :return: Данные пользователя.
        """
        header = request.headers.get(self._auth_header_name)
        if header is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        scheme, credential = header.split(" ")
        if not (scheme and credential):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
        return get_user_data(credential, self._public_key, self._alg)
