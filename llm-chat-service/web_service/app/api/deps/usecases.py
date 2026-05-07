from typing import Annotated

from fastapi import Depends, Request

from web_service.app.core.config import settings
from web_service.app.infra.rabbitmq import RabbitMQClient
from web_service.app.schemas.config import Settings
from web_service.app.usecases.admin import AdminUsecase
from web_service.app.usecases.auth import AuthUsecase
from web_service.app.usecases.chat import ChatUsecase
from web_service.app.usecases.stream_chat import StreamChatUsecase

from .services import AuthClientDep, ChatClientDep


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


def stream_chat_usecase(
        request: Request,
        chat_client: ChatClientDep
) -> StreamChatUsecase:
    """
    :param request: Запрос FastAPI.
    :param chat_client: Экземпляр класса ChatClient.
    :return: Экземпляр класса StreamChatUsecase.
    """
    rabbitmq_client: RabbitMQClient = request.app.state.rabbitmq_client
    settings: Settings = request.app.state.settings
    return StreamChatUsecase(
        rabbitmq_client,
        chat_client,
        settings.rabbitmq.message_queue
    )


def admin_usecase(chat_client: ChatClientDep) -> AdminUsecase:
    """
    :param chat_client: Экземпляр класса ChatClient.
    :return: Экземпляр класса AdminUsecase.
    """
    return AdminUsecase(chat_client)


AuthUsecaseDep = Annotated[AuthUsecase, Depends(auth_usecase)]
ChatUsecaseDep = Annotated[ChatUsecase, Depends(chat_usecase)]
StreamChatUsecaseDep = Annotated[
    StreamChatUsecase,
    Depends(stream_chat_usecase)
]
AdminUsecaseDep = Annotated[AdminUsecase, Depends(admin_usecase)]
