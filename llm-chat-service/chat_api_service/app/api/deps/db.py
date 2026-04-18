from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from chat_api_service.app.core.config import settings
from chat_api_service.app.db.session import DBSession
from chat_api_service.app.repositories.message import MessageRepository
from chat_api_service.app.repositories.conversation import (
    ConversationRepository)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    :yield: Подключения к базе данных.
    """
    if not DBSession.is_initialized:
        DBSession.setup(settings.db.database_url)

    async with DBSession.get_async_session() as session:
        yield session


def get_message_repo(
        session: Annotated[AsyncSession, Depends(get_db)],
) -> MessageRepository:
    """
    :param session: Сессия БД.
    :return: Экземпляр UserRepository.
    """
    return MessageRepository(session=session)


def get_conversation_repo(
        session: Annotated[AsyncSession, Depends(get_db)],
) -> ConversationRepository:
    """
    :param session: Сессия БД.
    :return: Экземпляр ConversationRepository.
    """
    return ConversationRepository(session=session)


MessagesRepoDep = Annotated[MessageRepository, Depends(get_message_repo)]
ConversationRepoDep = Annotated[
    ConversationRepository,
    Depends(get_conversation_repo)
]
