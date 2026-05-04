from web_service.app.usecases.auth import AuthUsecase
from fastapi import Depends
from typing import Annotated
from .services import AuthClientDep, ChatClientDep
from web_service.app.core.config import settings
from web_service.app.usecases.chat import ChatUsecase


def auth_usecase(auth_client: AuthClientDep) -> AuthUsecase:
    """
    :param auth_client: Экземпляр класса AuthClient.
    :return: Экземпляр класса AuthUsecase.
    """
    return AuthUsecase(auth_client, settings)


def chat_usecase(chat_client: ChatClientDep) -> ChatUsecase:
    """
    :param chat_client: Экземпляр класса ChatClient.
    :return: Экземпляр класса ChatUsecase.
    """
    return ChatUsecase(chat_client)


AuthUsecaseDep = Annotated[AuthUsecase, Depends(auth_usecase)]
ChatUsecaseDep = Annotated[ChatUsecase, Depends(chat_usecase)]
