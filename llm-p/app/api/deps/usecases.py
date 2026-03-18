from app.usecases.auth import AuthUseCase
from app.usecases.chat import ChatUseCase
from .db import UserRepoDependency, MessageRepoDependency
from . import OpenRouterClientDependency
from typing import Annotated

from fastapi import Depends


async def get_auth_usecase(user_repo: UserRepoDependency) -> AuthUseCase:
    """
    :param user_repo: Репозиторий для работы с таблицей пользователей.
    :return: Usecase для авторизации.
    """
    return AuthUseCase(user_repo)


async def get_chat_usecase(
        message_repo: MessageRepoDependency,
        openrouter_client: OpenRouterClientDependency
) -> ChatUseCase:
    """
    :param message_repo: Репозиторий для работы с таблицей сообщений чата.
    :param openrouter_client: Клиент для работы с OpenRouter API.
    :return: Usecase для работы с чатом.
    """
    return ChatUseCase(message_repo, openrouter_client)


AuthUsecaseDependency = Annotated[AuthUseCase, Depends(get_auth_usecase)]
ChatUsecaseDependency = Annotated[ChatUseCase, Depends(get_chat_usecase)]
