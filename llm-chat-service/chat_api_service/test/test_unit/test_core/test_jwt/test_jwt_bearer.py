from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, Request, status
from pytest_mock import MockerFixture

from chat_api_service.app.core import jwt
from libs.jwt_token.token_data import TokenUserData


@pytest.fixture
def bearer_instance():
    """
    Фикстура с настроенным экземпляром JWTBearer.

    :return: Экземпляр JWTBearer
    """
    return jwt.JWTBearer(
        public_key="test_public_key",
        alg="RS256",
        auth_header_name="Authorization"
    )


@pytest.fixture
def mock_request():
    """
    Фикстура с мок-объектом FastAPI Request.

    :return: Мок-объект Request.
    """
    request = MagicMock(spec=Request)
    return request


@pytest.mark.parametrize("header", [
    pytest.param("", id="empty"),
    pytest.param(" ", id="space"),
    pytest.param("Bearer ", id="no_token_with_space"),
    pytest.param("Bearer", id="no_token"),
    pytest.param("Token abc123", id="wrong_scheme"),

])
def test_fail_401(
        bearer_instance: jwt.JWTBearer,
        mock_request: MagicMock,
        header: str
):
    """
    Ошибка авторизации -> 401.

    :param bearer_instance: Экземпляр JWTBearer
    :param mock_request: Мок-объект Request.
    :param header: Заголовок запроса.
    """
    mock_request.headers.get.return_value = header

    with pytest.raises(HTTPException) as exc_info:
        bearer_instance(mock_request)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("bearer", [
    pytest.param("Bearer", id="capitalize"),
    pytest.param("bearer", id="lowercase"),
    pytest.param("BEARER", id="uppercase"),
])
def test_valid_token_returns_user_data(
        mocker: MockerFixture,
        bearer_instance,
        mock_request,
        bearer: str
):
    """
    Валидный заголовок -> вызов get_user_data и возврат данных

    :param mocker: Фикстура pytest-mocker.
    :param bearer_instance: Экземпляр JWTBearer.
    :param mock_request: Мок-объект Request.
    :param bearer: Схема авторизации.
    """
    mock_get_user_data = mocker.patch.object(jwt, "get_user_data")
    expected_user = TokenUserData(user_id=42, user_role="admin")
    mock_get_user_data.return_value = expected_user

    mock_request.headers.get.return_value = f"{bearer} valid_jwt_token"

    result = bearer_instance(mock_request)
    assert result == expected_user

    mock_get_user_data.assert_called_once()
