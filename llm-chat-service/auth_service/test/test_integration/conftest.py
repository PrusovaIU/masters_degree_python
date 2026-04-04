import pytest
import httpx
from fastapi import FastAPI
from auth_service.app.schemas import config
from auth_service.app.main import App
from asgi_lifespan import LifespanManager
from auth_service.app.consts.db import DBType


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
            host="",
            port=0,
            user="",
            db_name="",
            password="",
            schema="",
            test_db_path="test_db.sqlite",
            db_type=DBType.sqlite
        )
    )


@pytest.fixture(scope="session")
def app(settings: config.Settings) -> FastAPI:
    """
    Поднимает FastAPI приложение для интеграционных тестов.

    :param settings: Тестовые настройки приложения.
    :return: Приложение для тестов.
    """
    return App(settings).app


@pytest.fixture
async def client(app: FastAPI):
    """
    :param app: приложение для тестов.
    :return: Тестовый клиент для приложения.
    """
    transport = httpx.ASGITransport(app=app)
    async with LifespanManager(app):
        async with httpx.AsyncClient(transport=transport) as client:
            yield client
