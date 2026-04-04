import pytest
import httpx
from fastapi import FastAPI
from auth_service.app.schemas import config
from auth_service.app.main import App
from asgi_lifespan import LifespanManager
from auth_service.app.consts.db import DBType
from collections.abc import AsyncGenerator
from auth_service.app.db.session import DBSession
from auth_service.app.db.base import Base


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
            test_db_path=":memory:",
            db_type=DBType.sqlite
        )
    )


@pytest.fixture(scope="session")
async def app(settings: config.Settings) -> AsyncGenerator[App]:
    """
    Настройка приложения для тестов.

    :param settings: Тестовые настройки приложения.
    :return: Приложение для тестов.
    """
    _app = App(settings)
    yield _app
    if DBSession.is_initialized():
        async with DBSession.engine().begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
async def client(app: App):
    """
    :param app: приложение для тестов.
    :return: Тестовый клиент для приложения.
    """
    fastapi_app: FastAPI = app.app
    transport = httpx.ASGITransport(app=fastapi_app)
    async with LifespanManager(fastapi_app):
        async with httpx.AsyncClient(transport=transport) as client:
            yield client
