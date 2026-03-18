from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user import UserRepository
from app.repositories.chat_messages import ChatMessageRepository
from app.services.openrouter_client import OpenRouterClient
from app.db.session import AsyncSessionLocal


async def get_session() -> AsyncGenerator[AsyncSession]:
    """
    Создание ассинхронной сессии подключения к базе данных.
    После завершения работы сессия закрывается.

    :yields: Ассинхронная сессия подключения к базе данных
    :return: None.
    """
    async with AsyncSessionLocal() as session:
        yield session


async def get_user_repository(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> UserRepository:
    """
    :param session: Сессия подключения к базе данных.
    :return: Репозиторий для работы с таблицей пользователей.
    """
    return UserRepository(session)


async def get_chat_message_repository(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> ChatMessageRepository:
    """
    :param session: Сессия подключения к базе данных.
    :return: Репозиторий для работы с таблицей сообщений чата.
    """
    return ChatMessageRepository(session)


async def get_openrouter_client() -> OpenRouterClient:
    """
    :return: Клиент для работы с OpenRouter API.
    """
    return OpenRouterClient()


MessageRepoDependency = Annotated[
    ChatMessageRepository,
    Depends(get_chat_message_repository)
]
OpenRouterClientDependency = Annotated[
    OpenRouterClient,
    Depends(get_openrouter_client)
]
UserRepoDependency = Annotated[UserRepository, Depends(get_user_repository)]
