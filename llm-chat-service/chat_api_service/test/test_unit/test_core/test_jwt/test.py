from datetime import timedelta

import pytest

from chat_api_service.app.core.jwt import verify_access_token
from libs.jwt_token import create_access_token
from random import randint
from libs.jwt_token.exceptions import TokenError

USER_ID = randint(1, 10000)
USER_ROLE = "user"

SECRET_KEY = "test_secret"
ALG = "HS256"


def test_positive():
    """
    Позитивный тест. Проверка, что проходит верификация корректного токена.

    :return: None.
    """
    token: str = create_access_token(
        USER_ID,
        USER_ROLE,
        timedelta(minutes=10),
        SECRET_KEY,
        ALG,
        {"note": "test"}
    )
    verify_access_token(
        token,
        SECRET_KEY,
        ALG
    )


def test_negative():
    """
    Негативный тест. Проверка, что не проходит верификация
    некорректного токена.

    :return: None.
    """
    with pytest.raises(TokenError):
        verify_access_token("123", SECRET_KEY, ALG)
