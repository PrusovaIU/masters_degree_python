import pytest
from httpx import AsyncClient, Response

from auth_service.app.api.router_auth import refresh_token
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
LOGIN_DATA = {
    "username": EMAIL,
    "password": PASSWORD
}

ME_URL = "/auth/me"


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


async def _test_login(app: App, client: AsyncClient) -> (str, str):
    """
    Тестирование успешного логина.

    :param app: Тестируемое приложение.
    :param client: Тестовый клиент.
    :return: Access и refresh токены.
    """
    response: Response = await client.post(LOGIN_URL, data=LOGIN_DATA)
    response.raise_for_status()
    response_json = response.json()
    access_token = response_json["access_token"]
    assert access_token is not None
    refresh_token = response_json["refresh_token"]
    assert refresh_token is not None
    assert response_json["token_type"] == "bearer"
    assert (response_json["expires_in"] ==
            app.settings.jwt.access_expire.total_seconds())
    assert (response_json["refresh_expires_in"] ==
            app.settings.jwt.refresh_expire.total_seconds())
    return access_token, refresh_token


async def _test_login_fail(
        client: AsyncClient,
        username: str,
        password: str
) -> None:
    """
    Тестирование неуспешного логина.
    :param client: Тестовый клиент.
    :param username: Username.
    :param password: Пароль.
    :return: None.
    """
    data = {
        "username": username,
        "password": password
    }
    response: Response = await client.post(LOGIN_URL, data=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def _test_me(client: AsyncClient, access_token: str) -> None:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response: Response = await client.get(ME_URL, headers=headers)
    response.raise_for_status()
    response_json = response.json()
    assert response_json["id"] is not None
    assert response_json["email"] == EMAIL
    assert response_json["role"] == UserRole.user.value
    assert response_json["created_at"] is not None
    assert response_json["updated_at"] is not None


async def _test_me_fail(client: AsyncClient, access_token: str | None) -> None:
    headers = {}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    response: Response = await client.get(ME_URL, headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test(app: App, client: AsyncClient):
    await _test_register(client)
    await _test_register_conflict(client)
    access_token, refresh_token = await _test_login(app, client)
    # Логин с неверным паролем:
    await _test_login_fail(client, EMAIL, "wrong_password")
    # Логин с неизвестным email:
    await _test_login_fail(client, "unknown@test.com", PASSWORD)
    await _test_me(client, access_token)
    # ME с невалидным access token:
    await _test_me_fail(client, refresh_token)
    # ME без токена:
    await _test_me_fail(client, None)
