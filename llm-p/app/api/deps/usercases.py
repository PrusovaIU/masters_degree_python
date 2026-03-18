from app.usercases.auth import AuthUseCase
from app.usercases.chat import ChatUseCase
from .db import UserRepoDependency, MessageRepoDependency, OpenRouterClientDependency
from typing import Annotated

from fastapi import Depends


async def get_auth_usercase(user_repo: UserRepoDependency) -> AuthUseCase:
    """
    :param user_repo: Репозиторий для работы с таблицей пользователей.
    :return: Usercase для авторизации.
    """
    return AuthUseCase(user_repo)


async def get_chat_usercase(
        message_repo: MessageRepoDependency,
        openrouter_client: OpenRouterClientDependency
) -> ChatUseCase:
    """
    :param message_repo: Репозиторий для работы с таблицей сообщений чата.
    :param openrouter_client: Клиент для работы с OpenRouter API.
    :return: Usercase для работы с чатом.
    """
    return ChatUseCase(message_repo, openrouter_client)


AuthUsercaseDependency = Annotated[AuthUseCase, Depends(get_auth_usercase)]
ChatUsercaseDependency = Annotated[ChatUseCase, Depends(get_chat_usercase)]
