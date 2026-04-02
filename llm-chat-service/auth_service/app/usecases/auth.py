from sqlalchemy.exc import IntegrityError

from auth_service.app.schemas.user import UserPublic
from auth_service.app.consts.user_role import UserRole
from auth_service.app.schemas import auth as auth_schemas
from auth_service.app.core.exceptions import users as users_exc, security as security_exc
from auth_service.app.core.security.password import PWDContext
from auth_service.app.repositories.users import UserRepository
from loguru import logger
from auth_service.app.db.models import User
from auth_service.app.core.security import jwt_token
from auth_service.app.schemas.config import JWTConfig
from auth_service.app.consts.token_type import TokenType


class AuthUseCase:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def register(
            self,
            email: str,
            password: str,
            role: UserRole
    ) -> UserPublic:
        """
        Регистрирует нового пользователя в системе.

        :param email: Email пользователя.
        :param password: Пароль в открытом виде.
        :param role: Роль пользователя.

        :return: Данные нового пользователя.

        :raises UserAlreadyExistsError: Если пользователь с таким email уже
            существует.
        """
        try:
            password_hash = PWDContext.hash_password(password)
            user: User = await self._user_repo.create(
                email=email,
                password_hash=password_hash,
                role=role
            )
            user_data = UserPublic.model_validate(user)
        except IntegrityError as err:
            logger.error(
                f"Пользователь с email {email} уже существует ({err})"
            )
            raise users_exc.UserAlreadyExistsError(f"{email}")
        except Exception as err:
            logger.error(
                f"Ошибка при регистрации пользователя: {err} "
                f"({err.__class__.__name__})"
            )
            raise
        return user_data

    async def login(
            self,
            email: str,
            password: str,
            jwt_config: JWTConfig
    ) -> tuple[str, str]:
        """
        Аутентификация пользователя.

        :param email: Email пользователя.
        :param password: Пароль в открытом виде.
        :param jwt_config: Конфигурация JWT.

        :return: access_token, refresh_token

        :raises InvalidCredentialsError: Если пользователь не найден или
            передан неверный пароль.

        :raises SecurityError: При непредвиденной ошибке.
        """
        try:
            user: User | None = await self._user_repo.get_by_email(email)
            if user is None:
                raise security_exc.InvalidCredentialsError()

            if not PWDContext.verify_password(password, user.password_hash):
                raise security_exc.InvalidCredentialsError()

            access_token: str = jwt_token.create_access_token(
                user.id,
                user.role.value,
                jwt_config.access_expire,
                jwt_config.access_secret,
                jwt_config.alg
            )
            refresh_token: str = jwt_token.create_refresh_token(
                user.id,
                jwt_config.refresh_expire,
                jwt_config.refresh_secret,
                jwt_config.alg
            )
        except security_exc.InvalidCredentialsError as err:
            logger.warning(str(err))
            raise
        except Exception as err:
            err_title = "Ошибка при аутентификации пользователя"
            logger.error(
                f"{err_title}: {err} ({err.__class__.__name__})"
            )
            raise security_exc.SecurityError(err_title) from err
        return access_token, refresh_token

    async def get_current_user(
            self,
            token: str,
            token_type: TokenType,
            secret: str,
            alg: str,
            verify_exp: bool = True
    ) -> UserPublic:
        """
        Получение текущего пользователя по JWT токену.

        :param token: Токен.
        :param token_type: Тип токена.
        :param secret: Ключ для подписи.
        :param alg: Алгоритм шифрования подписи.
        :param verify_exp: Проверять ли срок действия токена.

        :return: Данные пользователя из БД.

        :raises TokenExpiredError: Если срок действия токена истек.
        :raises InvalidTokenError: Если токен не прошел валидацию.
        :raises TokenDecodeError: Если токен не может быть декодирован.
        :raises UserNotFoundError: Если пользователь из токена не найден в БД.
        """
        token_data: jwt_token.TokenDataT = jwt_token.verify_token(
            token,
            token_type,
            secret,
            alg,
            verify_exp
        )
        user_id = int(token_data.sub)
        user: User | None = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise users_exc.UserNotFoundError(f"ID = {user_id}")
        return UserPublic.model_validate(user)

    async def me(
            self,
            access_token: str,
            jwt_config: JWTConfig,
    ) -> UserPublic:
        """
        Получение профиля текущего пользователя.

        :param access_token: JWT access текущего пользователя.
        :param jwt_config: Конфигурация JWT.

        :return: Данные пользователя.

        :raises TokenExpiredError: Если срок действия токена истек.
        :raises InvalidTokenError: Если токен не прошел валидацию.
        :raises TokenDecodeError: Если токен не может быть декодирован.
        :raises UserNotFoundError: Если пользователь из токена не найден в БД.
        :raises GetUserError: При непредвиденной ошибке.
        """
        try:
            user: UserPublic = await self.get_current_user(
                access_token,
                TokenType.access,
                jwt_config.access_secret,
                jwt_config.alg,
                False
            )
        except Exception as err:
            err_title = "Ошибка при получении профиля пользователя"
            logger.error(f"{err_title}: {err} ({err.__class__.__name__})")
            raise users_exc.GetUserError(err_title) from err
        return user

    async def refresh_token(
            self,
            refresh_token: str,
            jwt_config: JWTConfig
    ) -> str:
        """
        Обновление access токена на основе refresh токена.

        :param refresh_token: JWT refresh токен.
        :param jwt_config: Конфигурация JWT.

        :return: Новый access токен.

        :raises TokenExpiredError: Если срок действия токена истек.
        :raises InvalidTokenError: Если токен не прошел валидацию.
        :raises TokenDecodeError: Если токен не может быть декодирован.
        :raises UserNotFoundError: Если пользователь из токена не найден в БД.
        :raises AuthError: При непредвиденной ошибке.
        """
        try:
            user: UserPublic = await self.get_current_user(
                refresh_token,
                TokenType.refresh,
                jwt_config.refresh_secret,
                jwt_config.alg
            )
            new_access_token: str = jwt_token.create_access_token(
                user.id,
                user.role,
                jwt_config.access_expire,
                jwt_config.access_secret,
                jwt_config.alg
            )
        except Exception as err:
            err_title = "Ошибка обновления access токена"
            logger.error(f"{err_title}: {err} ({err.__class__.__name__})")
            raise security_exc.SecurityError(err_title) from err
        return new_access_token
