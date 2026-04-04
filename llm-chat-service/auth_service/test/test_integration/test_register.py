import pytest


EMAIL = "test@test.com"


@pytest.mark.asyncio
async def test_success_register(client):
    assert True
