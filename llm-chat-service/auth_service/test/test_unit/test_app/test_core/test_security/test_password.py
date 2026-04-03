from auth_service.app.core.security.password import PWDContext
import pytest

PWDContextType = type[PWDContext]


TEST_PASSWORD = "P@ssw0rd!"
TEST_WRONG_PASSWORD = "WrongP@ssw0rd!"


@pytest.fixture(scope="session")
def pwd_context() -> PWDContextType:
    """
    Фикстура для инициализации контекста пароля.

    :return: Класс контекста пароля.
    """
    PWDContext.setup()
    return PWDContext


def test_positive(pwd_context: PWDContextType):
    """
    Позитивный тест. Пароль соответствует хешу.

    :param pwd_context: Инициализированный контекст пароля.
    """
    hashed_password = pwd_context.hash_password(TEST_PASSWORD)
    success = pwd_context.verify_password(TEST_PASSWORD, hashed_password)
    assert success is True
    assert hashed_password != TEST_PASSWORD


def test_negative(pwd_context: PWDContextType):
    """
    Негативный тест. Пароль не соответствует хешу.

    :param pwd_context: Инициализированный контекст пароля.
    """
    hash_password = pwd_context.hash_password(TEST_PASSWORD)
    success = pwd_context.verify_password(
        TEST_WRONG_PASSWORD, hash_password
    )
    assert success is False

def test_hash_password_is_deterministic_for_verification(
        pwd_context: PWDContextType
):
    """
    Один и тот же пароль даёт разные хеши, но оба верифицируются.

    :param pwd_context: Инициализированный контекст пароля.
    """
    hash1 = PWDContext.hash_password(TEST_PASSWORD)
    hash2 = PWDContext.hash_password(TEST_PASSWORD)

    assert hash1 != hash2
    assert PWDContext.verify_password(TEST_PASSWORD, hash1)
    assert PWDContext.verify_password(TEST_PASSWORD, hash2)
