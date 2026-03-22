from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.db.models import User
from app.core.errors import user as user_errors
from loguru import logger


class UserRepository:
    """Репозиторий для работы с таблицей user"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: int) -> User | None:
        """
        Получить пользователя по ID.

        :param user_id: ID пользователя.

        :return: пользователь, если найден, иначе None.

        :raises UserNotFound: Если пользователь не найден.
        """
        user: User | None = await self._session.get(User, user_id)
        if not user:
            err_txt = f"user_id={user_id}"
            logger.error(f"Unknown user {err_txt}")
            raise user_errors.UserNotFound(err_txt)
        return user


    async def get_by_email(self, email: str) -> User:
        """
        Получить пользователя по email.

        :param email: Email пользователя

        :return: Данные пользователя.

        :raises UserNotFound: Если пользователь не найден.
        """
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        user: User | None = result.scalar_one_or_none()
        if not user:
            err_txt = f"email={email}"
            logger.warning(f"Unknown user {err_txt}")
            raise user_errors.UserNotFound(err_txt)
        return user

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

        :return: Созданный пользователь.
        """
        user = User(
            email=email,
            password_hash=password_hash,
            role=role
        )
        try:
            self._session.add(user)
            await self._session.commit()
            await self._session.refresh(user)
        except IntegrityError as err:
            err_txt = f"email={email}, role={role}"
            logger.error(f"User already exists {err_txt}")
            raise user_errors.UserAlreadyExists(err_txt) from err
        except SQLAlchemyError as err:
            err_txt = f"email={email}, role={role}"
            logger.error(f"Failed to create user {err_txt} "
                         f"({err.__class__.__name__})")
            raise user_errors.CreateUserError(err_txt) from err
        return user
