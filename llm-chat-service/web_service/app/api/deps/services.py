from web_service.app.services.auth_client import AuthClient
from web_service.app.core.config import settings
from typing import Annotated
from fastapi import Depends
from web_service.app.services.chat_client import ChatAPIServiceClient


def get_auth_client() -> AuthClient:
    """
    :return: Экземпляр клиента для работы с сервисом авторизации
    """
    return AuthClient(
        settings.auth_service.url,
        settings.auth_service.timeout,
        settings.auth_header_name
    )


def get_chat_client() -> ChatAPIServiceClient:
    """
    :return: Экземпляр клиента для работы с сервисом чата.
    """
    return ChatAPIServiceClient(
        settings.chat_api_service.url,
        settings.chat_api_service.timeout,
        settings.auth_header_name
    )


AuthClientDep = Annotated[AuthClient, Depends(get_auth_client)]
ChatClientDep = Annotated[ChatAPIServiceClient, Depends(get_chat_client)]
