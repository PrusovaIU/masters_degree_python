import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from auth_service.app.schemas import config
from auth_service.app.main import App


@pytest.fixture(scope="session")
def settings() -> config.Settings:
    """
    :return: Тестовые настройки приложения.
    """
    return config.Settings(
        jwt=config.JWTConfig(
            access_secret=config.JWTSecret(data="test_access_secret"),
            refresh_secret=config.JWTSecret(data="test_refresh_secret")
        ),
        db=config.DatabaseConfig(
            host="127.0.0.1",
            port=5432,
            user="postgres",
            db_name="postgres",
            password="123456",
            schema="test_auth_service"
        )
    )


@pytest.fixture(scope="session")
def app(settings: config.Settings) -> FastAPI:
    """
    Поднимает FastAPI приложение для интеграционных тестов.

    :param settings: тестовые настройки приложения.
    :return: приложение для тестов.
    """
    return App(settings).app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """
    :param app: приложение для тестов.
    :return: тестовый клиент для приложения.
    """
    return TestClient(app)
