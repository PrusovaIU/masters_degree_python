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

    def __call__(self, request: Request) -> TokenUserData:
        """
        Проверка валидности токена.

        :param request: Запрос.
        :return: Данные пользователя.
        """
        scheme, credential = self._get_scheme_and_credential(request)
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
        return get_user_data(credential, self._public_key, self._alg)

    def _get_scheme_and_credential(self, request: Request) -> tuple[str, str]:
        """
        Получение схемы и credential из заголовка.

        :param request: Запрос.
        :return: Схема и credential.
        """
        header = request.headers.get(self._auth_header_name)
        if header is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        parts = header.split(maxsplit=1)
        if len(parts) != 2:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Not authenticated")

        scheme, credential = parts
        return scheme, credential
