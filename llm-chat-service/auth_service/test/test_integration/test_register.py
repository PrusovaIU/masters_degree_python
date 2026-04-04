import pytest
from httpx import AsyncClient, Response
from auth_service.app.consts.user_role import UserRole


EMAIL = "test@test.com"
URL = "/auth/register"


@pytest.mark.asyncio
async def test_positive(client: AsyncClient):
    body = {
        "email": EMAIL,
        "password": "P@ssword123"
    }
    response: Response = await client.post(URL, json=body)
    response.raise_for_status()
    response_json = response.json()
    assert response_json["email"] == EMAIL
    assert response_json["user_id"] is not None
    assert response_json["role"] == UserRole.user.value
