from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from auth_service.app.core.exceptions import password as passwd_errors

import jwt
from passlib.context import CryptContext
from loguru import logger

from auth_service.app.core.config import settings


_PWD_CONTEXT = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


def hash_password(password: str) -> str:
    """
    Хеширование пароля с использованием bcrypt.

    :param password: Пароль в открытом виде.

    :return: Хешированный пароль.

    :raises PasswordHashError: Если хеширование не удалось.
    """
    try:
        return _PWD_CONTEXT.hash(password)
    except Exception as err:
        logger.error(f"Ошибка хеширования пароля: {err}")
        raise passwd_errors.PasswordHashError(
            "Не удалось хешировать пароль"
        ) from err


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Проверка соответствия пароля и хеша.

    :param password: Пароль в открытом виде.
    :param hashed_password: Хешированный пароль.
    :return: True, если пароль соответствует хешу, иначе False.

    :raises HashFormatError: Если формат хеша не поддерживается.

    :raises VerifyPasswordError: Если при проверке произошла ошибка.
    """
    try:
        return _PWD_CONTEXT.verify(password, hashed_password)
    except ValueError as err:
        err_title = "Неверный формат хеша пароля"
        logger.error(f"{err_title}: {err}")
        raise passwd_errors.HashFormatError(err_title) from err
    except Exception as err:
        err_title = "Ошибка при проверке пароля"
        logger.error(f"{err_title}: {err}")
        raise passwd_errors.VerifyPasswordError(err_title) from err
