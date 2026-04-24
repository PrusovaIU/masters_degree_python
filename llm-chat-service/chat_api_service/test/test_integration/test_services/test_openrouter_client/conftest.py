import pytest

from chat_api_service.app.schemas.config import OpenRouterConfig
from chat_api_service.app.services.openrouter_client import OpenRouterClient


@pytest.fixture
def openrouter_config():
    """
    Фикстура с тестовыми настройками OpenRouter.

    :return: Тестовые настройки OpenRouter.
    """
    return OpenRouterConfig(
        api_key="test-api-key-12345",
        referer="https://test-app.local",
        base_url="https://openrouter.ai/api/v1",
        model="test/model:free",
        app_name="test-app",
        title="test-request",
        request_timeout=10,
    )


@pytest.fixture
def openrouter_client(openrouter_config):
    """
    Фикстура клиента OpenRouter.

    :param openrouter_config: Тестовые настройки OpenRouter.
    :return: Клиент OpenRouter.
    """
    return OpenRouterClient(settings=openrouter_config)
