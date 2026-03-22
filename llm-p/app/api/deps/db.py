from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.repositories.chat_messages import ChatMessageRepository
from app.repositories.user import UserRepository


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


MessageRepoDependency = Annotated[
    ChatMessageRepository,
    Depends(get_chat_message_repository)
]
UserRepoDependency = Annotated[UserRepository, Depends(get_user_repository)]
