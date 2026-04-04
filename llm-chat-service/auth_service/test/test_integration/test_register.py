import pytest
from httpx import AsyncClient, Response
from auth_service.app.consts.user_role import UserRole
from fastapi import status
from auth_service.app.app import App


EMAIL = "test@test.com"
PASSWORD = "P@ssword123"

REGISTER_URL = "/auth/register"
REGISTER_BODY = {
    "email": EMAIL,
    "password": PASSWORD,
}

LOGIN_URL = "/auth/login"
LOGIN_BODY = {
    "username": EMAIL,
    "password": PASSWORD
}


async def _test_register(client: AsyncClient) -> None:
    """
    Тестирование успешной регистрации.

    :param client: Тестовый клиент.
    """
    response: Response = await client.post(REGISTER_URL, json=REGISTER_BODY)
    response.raise_for_status()
    response_json = response.json()
    assert response_json["email"] == EMAIL
    assert response_json["user_id"] is not None
    assert response_json["role"] == UserRole.user.value


async def _test_register_conflict(client: AsyncClient) -> None:
    """
    Тестирование регистрации с существующим email.

    :param client: Тестовый клиент.
    """
    response: Response = await client.post(REGISTER_URL, json=REGISTER_BODY)
    assert response.status_code == status.HTTP_409_CONFLICT


async def _test_login(app: App, client: AsyncClient) -> None:
    """
    Тестирование успешного логина.

    :param app: Тестируемое приложение.
    :param client: Тестовый клиент.
    :return: None.
    """
    response: Response = await client.post(LOGIN_URL, data=LOGIN_BODY)
    response.raise_for_status()
    response_json = response.json()
    assert response_json["access_token"] is not None
    assert response_json["refresh_token"] is not None
    assert response_json["token_type"] == "bearer"
    assert (response_json["expires_in"] ==
            app.settings.jwt.access_expire.total_seconds())
    assert (response_json["refresh_expires_in"] ==
            app.settings.jwt.refresh_expire.total_seconds())


@pytest.mark.asyncio
async def test(app: App, client: AsyncClient):
    await _test_register(client)
    await _test_register_conflict(client)
    await _test_login(app, client)
