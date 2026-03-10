import hashlib
import hmac
import secrets

from app.core.config import SETTINGS
from loguru import logger



_HASH_ALGORITHM = "sha256"  # Алгоритм хеширования пароля
# Формат хеша пароля:
_PASSWD_HASH_FORMAT = "{iterations}${algorithm}${salt}${hash}"


def _generate_hash(
        password: bytes,
        salt: bytes,
        iterations: int = SETTINGS.password.pbkdf2_iterations
) -> bytes:
    """
    Генерация хеша пароля.

    :param password: Пароль в открытом виде.
    :param salt: Соль.
    :param iterations: Количество итераций.
    :return: Хеш пароля.
    """
    return hashlib.pbkdf2_hmac(
        _HASH_ALGORITHM,
        password,
        salt,
        iterations,
        dklen=SETTINGS.password.hash_len
    )


def get_password_hash(password: str) -> str:
    """
    Хеширование пароля алгоритмом SHA256

    :param password: Пароль в открытом виде.

    :return: Хеш пароля в hex формате iterations$algorithm$salt$hash
    """
    salt: str = secrets.token_hex(SETTINGS.password.salt_len)
    salt_bytes = bytes.fromhex(salt)
    key = _generate_hash(password.encode("utf-8"), salt_bytes)
    password_hash = _PASSWD_HASH_FORMAT.format(
        iterations=SETTINGS.password.pbkdf2_iterations,
        algorithm=_HASH_ALGORITHM,
        salt=salt,
        hash=key.hex()
    )
    return password_hash


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Верификация пароля.

    :param plain_password: Пароль в открытом виде.

    :param hashed_password: Хешированный пароль в формате
        iterations$algorithm$salt$hash.

    :return: True если пароль верен, иначе False.
    """
    try:
        iterations_str, algorithm, salt, original_hash = (
            hashed_password.split("$")
        )
        iterations = int(iterations_str)

        if algorithm != _HASH_ALGORITHM:
            return False

        salt_bytes = bytes.fromhex(salt)
        key: bytes = _generate_hash(
            plain_password.encode("utf-8"), salt_bytes, iterations
        )
        computed_hash = key.hex()
        return hmac.compare_digest(computed_hash, original_hash)

    except (ValueError, KeyError, IndexError) as err:
        logger.error(f"Cannot verify password: {err}")
        return False
