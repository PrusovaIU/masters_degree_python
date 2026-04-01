from collections.abc import Callable

from auth_service.app.core.exceptions import password as passwd_errors

from passlib.context import CryptContext
from loguru import logger
from functools import wraps


class PWDContext:
    _pwd_context: CryptContext | None = None

    @classmethod
    def setup(cls, schemes: list[str] = None, bcrypt_rounds: int = 12):
        if not schemes:
            schemes = ["bcrypt"]
        cls._pwd_context = CryptContext(
            schemes=schemes,
            deprecated="auto",
            bcrypt__rounds=bcrypt_rounds
        )
        logger.info("Установлен контекст для хеширования паролей")

    @staticmethod
    def _check_setup(class_method: Callable):
        @wraps(class_method)
        def wrapper(cls, *args, **kwargs):
            if not cls._pwd_context:
                raise SystemError(
                    "Контекст для хеширования не установлен. "
                    "Используйте setup()"
                )
            return class_method(cls, *args, **kwargs)
        return wrapper

    @classmethod
    @_check_setup
    def hash_password(cls, password: str) -> str:
        """
        Хеширование пароля с использованием bcrypt.

        :param password: Пароль в открытом виде.

        :return: Хешированный пароль.

        :raises PasswordHashError: Если хеширование не удалось.
        """
        try:
            return cls._pwd_context.hash(password)
        except Exception as err:
            logger.error(f"Ошибка хеширования пароля: {err}")
            raise passwd_errors.PasswordHashError(
                "Не удалось хешировать пароль"
            ) from err

    @classmethod
    @_check_setup
    def verify_password(cls, password: str, hashed_password: str) -> bool:
        """
        Проверка соответствия пароля и хеша.

        :param password: Пароль в открытом виде.
        :param hashed_password: Хешированный пароль.
        :return: True, если пароль соответствует хешу, иначе False.

        :raises HashFormatError: Если формат хеша не поддерживается.

        :raises VerifyPasswordError: Если при проверке произошла ошибка.
        """
        try:
            return cls._pwd_context.verify(password, hashed_password)
        except ValueError as err:
            err_title = "Неверный формат хеша пароля"
            logger.error(f"{err_title}: {err}")
            raise passwd_errors.HashFormatError(err_title) from err
        except Exception as err:
            err_title = "Ошибка при проверке пароля"
            logger.error(f"{err_title}: {err}")
            raise passwd_errors.VerifyPasswordError(err_title) from err
