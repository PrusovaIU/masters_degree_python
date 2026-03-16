from app.db.models import User
from app.repositories.user import UserRepository
from app.core.security.password import verify_password, get_password_hash
from app.core.security.jwt_token import create_access_token
from app.schemas.user import UserPublic
from app.core.errors import usercase_auth as errors
from app.core.config import settings
from loguru import logger


class AuthUseCase:
    """Usecase для аутентификации и управления пользователями."""

    def __init__(self, user_repository: UserRepository):
        self._user_repo = user_repository

    async def register(
            self,
            email: str,
            password: str,
            role: str
    ) -> UserPublic:
        """
        Зарегистрировать нового пользователя.

        :param email: Email пользователя.
        :param password: Пароль.
        :param role: Роль пользователя.

        :return: Данные созданного пользователя.

        :raises UserAlreadyExistsError: Если пользователь с таким email уже
            существует.
        """
        existing_user: User | None = await self._user_repo.get_by_email(email)
        if existing_user:
            logger.warning(f"User with email {email} already exists")
            raise errors.UserAlreadyExistsError(email)
        password_hash: str = get_password_hash(password)
        user: User = await self._user_repo.create(
            email=email,
            password_hash=password_hash,
            role=role
        )
        return UserPublic.model_validate(user)

    async def login(self, email: str, password: str) -> str:
        """
        Аутентифицировать пользователя и получить JWT токен.

        :param email: Email пользователя.
        :param password: Пароль.

        :return: JWT токен.

        :raises InvalidCredentialsError: Если email не существует или
            пароль неверный.
        """
        user: User | None = await self._user_repo.get_by_email(email)
        if not user:
            logger.warning(f"Unknown email: {email}")
            raise errors.InvalidCredentialsError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            logger.warning(f"Invalid password for email: {email}")
            raise errors.InvalidCredentialsError("Invalid email or password")

        access_token: str = create_access_token(
            user.id,
            user.role,
            settings.jwt.access_token_expire
        )

        return access_token

    async def get_profile(self, user_id: int) -> UserPublic:
        """
        Получить профиль пользователя по ID.

        :param user_id: ID пользователя

        :return: Данные пользователя

        :raises UserNotFoundError: Если пользователь не найден
        """
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            logger.warning(f"User with id {user_id} not found")
            raise errors.UserNotFoundError(str(user_id))

        return UserPublic.model_validate(user)