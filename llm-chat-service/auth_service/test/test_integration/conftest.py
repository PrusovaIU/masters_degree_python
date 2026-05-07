from os import environ

import httpx
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI

from auth_service.app.db.base import Base
from auth_service.app.db.session import DBSession
from auth_service.app.schemas import config
from libs.consts.db import DBType

environ.update({
    "JWT__ACCESS_SECRET__DATA": "test_access_secret",
    "JWT__REFRESH_SECRET__DATA": "test_access_secret",

    "DB__HOST": "",
    "DB__PORT": "0",
    "DB__USER": "",
    "DB__PASSWORD": "",
    "DB__DB_NAME": "",
    "DB__DB_SCHEMA": "",
    "DB__DB_TYPE": DBType.sqlite.value,
    "DB__TEST_DB_PATH": ":memory:",

    "LOGS__FILE_PATH": ""
})


@pytest.fixture(scope="session")
def settings() -> config.Settings:
    """
    :return: Тестовые настройки приложения.
    """
    from auth_service.app.core.config import settings
    return settings


@pytest.fixture(scope="session")
async def app(settings: config.Settings):
    """
    Настройка приложения для тестов.

    :param settings: Тестовые настройки приложения.
    :return: Приложение для тестов.
    """
    from auth_service.app.app import App
    _app = App(settings)
    yield _app
    if DBSession.is_initialized():
        async with DBSession.engine().begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
async def client(app):
    """
    :param app: приложение для тестов.
    :return: Тестовый клиент для приложения.
    """
    fastapi_app: FastAPI = app.app
    transport = httpx.ASGITransport(app=fastapi_app)
    async with LifespanManager(fastapi_app):
        async with httpx.AsyncClient(
                transport=transport,
                base_url="http://test"
        ) as client:
            yield client
