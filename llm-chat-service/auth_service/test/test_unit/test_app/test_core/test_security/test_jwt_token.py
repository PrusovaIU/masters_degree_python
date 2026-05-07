from datetime import datetime, timedelta
from time import sleep

import pytest

from libs import jwt_token
from libs.jwt_token import exceptions as exceptions
from libs.jwt_token.consts import TokenType
from libs.jwt_token.token_data import AccessTokenData, RefreshTokenData

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
    assert token_data.sub == str(subject)
    assert isinstance(token_data.exp, datetime)
    assert isinstance(token_data.iat, datetime)
    assert token_data.role == ROLE


@pytest.mark.parametrize("subject", SUBJECT_PARAMS)
def test_refresh_token(subject: str | int):
    token = jwt_token.create_refresh_token(
        subject,
        EXPIRES_DELTA,
        SECRET_KEY,
        ALG
    )
    token_data = jwt_token.verify_token(
        token,
        TokenType.refresh,
        SECRET_KEY,
        ALG
    )
    assert isinstance(token_data, RefreshTokenData)
    assert token_data.sub == str(subject)
    assert isinstance(token_data.exp, datetime)
    assert isinstance(token_data.iat, datetime)


def test_expired_token():
    """
    При верификации токена с истекшим сроком действия должно пробрасываться
    исключение.
    """
    token = jwt_token.create_access_token(
        SUBJECT_STR,
        ROLE,
        timedelta(seconds=1),
        SECRET_KEY,
        ALG
    )
    sleep(2)
    with pytest.raises(exceptions.TokenExpiredError):
        jwt_token.verify_token(
            token,
            TokenType.access,
            SECRET_KEY,
            ALG
        )
