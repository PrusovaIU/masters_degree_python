from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class UserRepository:
    """Репозиторий для работы с таблицей user"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: int) -> User | None:
        """
        Получить пользователя по ID.

        :param user_id: ID пользователя.

        :return: пользователь, если найден, иначе None.
        """
        return await self._session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        """
        Получить пользователя по email.

        :param email: Email пользователя

        :return: пользователь, если найден, иначе None.
        """
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
            self,
            email: str,
            password_hash: str,
            role: str
    ) -> User:
        """
        Создать нового пользователя.

        :param email: Email пользователя.
        :param password_hash: Хеш пароля.
        :param role: Роль пользователя.

        :return: созданный пользователь.
        """
        user = User(
            email=email,
            password_hash=password_hash,
            role=role
        )
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user
