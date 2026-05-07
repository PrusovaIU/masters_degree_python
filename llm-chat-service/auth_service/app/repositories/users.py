from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.app.consts.user_role import UserRole
from auth_service.app.db.models import User


class UserRepository:
    """
    Репозиторий для операций с таблицей пользователей.

    :param session: Асинхронная сессия SQLAlchemy.
    """
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: int) -> User | None:
        """
        Поиск пользователя по id.

        :param user_id: Числовой ID пользователя.
        :return: Экземпляр User, если найден, иначе None.

        :raises DBAPIError: Если возникла ошибка на уровне драйвера БД.
        """
        return await self._session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        """
        Поиск пользователя по email.

        :param email: Email пользователя.
        :return: Экземпляр User, если найден, иначе None.

        :raises DBAPIError: Если возникла ошибка на уровне драйвера БД.
        """
        stmt = select(User).where(
            func.lower(User.email) == func.lower(email)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
            self,
            email: str,
            password_hash: str,
            role: UserRole | str
    ) -> User:
        """
        Создание нового пользователя.

        :param email: Email пользователя (должен быть уникальным).
        :param password_hash: Хеш пароля.
        :param role: Роль пользователя.
        :return: Созданный экземпляр User с заполненным id.

        :raises DBAPIError: Если возникла критическая ошибка БД.
        """
        if isinstance(role, str):
            role = UserRole(role)
        user = User(
            email=email,
            password_hash=password_hash,
            role=role,
        )
        self._session.add(user)
        await self._session.flush()
        return user
