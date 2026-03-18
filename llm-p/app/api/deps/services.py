from typing import Annotated

from fastapi import Depends

from app.services.openrouter_client import OpenRouterClient


async def get_openrouter_client() -> OpenRouterClient:
    """
    :return: Клиент для работы с OpenRouter API.
    """
    return OpenRouterClient()


OpenRouterClientDependency = Annotated[
    OpenRouterClient,
    Depends(get_openrouter_client)
]
