from auth_service.app.core.security.password import PWDContext
import pytest

PWDContextType = type[PWDContext]


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
    password = "test_password"
    hashed_password = pwd_context.hash_password(password)
    success = pwd_context.verify_password(password, hashed_password)
    assert success is True


def test_negative(pwd_context: PWDContextType):
    """
    Негативный тест. Пароль не соответствует хешу.

    :param pwd_context: Инициализированный контекст пароля.
    """
    hash_password = pwd_context.hash_password("test_password")
    success = pwd_context.verify_password(
        "test_password2", hash_password
    )
    assert success is False
