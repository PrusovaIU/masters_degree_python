from web_service.app.services.auth_client import AuthClient
from web_service.app.core.config import settings
from typing import Annotated
from fastapi import Depends


def get_auth_client():
    """
    :return: Экземпляр клиента для работы с сервисом авторизации
    """
    return AuthClient(
        settings.auth_service.url,
        settings.auth_service.timeout,
        settings.auth_header_name
    )


AuthClientDep = Annotated[AuthClient, Depends(get_auth_client)]
