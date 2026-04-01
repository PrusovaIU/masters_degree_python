from auth_service.app.core.security import jwt_token
import pytest
from datetime import timedelta
from auth_service.app.consts.token_type import TokenType
from auth_service.app.schemas.token_data import AccessTokenData


SUBJECT_STR = "test_subject"
SUBJECT_INT = 123456

SUBJECT_PARAMS = [
    pytest.param(SUBJECT_STR, id="str"),
    pytest.param(SUBJECT_INT, id="int"),
]

ROLE = "test_role"
EXPIRES_DELTA = timedelta(minutes=15)
SECRET_KEY = "test_secret_key"
ALG = "HS256"

@pytest.mark.parametrize("subject", SUBJECT_PARAMS)
@pytest.mark.parametrize("payload", [
    pytest.param(None, id="None"),
    pytest.param({"test": "test"}, id="dict"),
])
def test_access_token(
        subject: str | int,
        payload: dict | None
):
    """
    Тест создания и верификации токена.

    :param subject: Идентификатор пользователя.
    :param payload: Дополнительные данные.
    :return: None.
    """
    token = jwt_token.create_access_token(
        subject,
        ROLE,
        EXPIRES_DELTA,
        SECRET_KEY,
        ALG,
        payload
    )
    token_data = jwt_token.verify_token(
        token,
        TokenType.access,
        SECRET_KEY,
        ALG
    )
    assert isinstance(token_data, AccessTokenData)
