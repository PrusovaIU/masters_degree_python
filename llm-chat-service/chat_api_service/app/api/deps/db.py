from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from chat_api_service.app.core.config import settings
from chat_api_service.app.db.session import DBSession


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    :yield: Подключения к базе данных.
    """
    if not DBSession.is_initialized:
        DBSession.setup(settings.db.database_url)

    async with DBSession.get_async_session() as session:
        yield session


def get_users_repo(
        session: Annotated[AsyncSession, Depends(get_db)],
) -> UserRepository:
    """
    :param session: Сессия БД.
    :return: Экземпляр UserRepository.
    """
    return UserRepository(session=session)


UserRepoDep = Annotated[UserRepository, Depends(get_users_repo)]
