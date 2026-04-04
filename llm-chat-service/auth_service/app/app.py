from typing import AsyncGenerator

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from auth_service.app.api import routers
from auth_service.app.core.security.password import PWDContext
from auth_service.app.db.base import Base
from auth_service.app.db.session import DBSession
from auth_service.app.schemas.config import Settings


class App:
    def __init__(self, config: Settings):
        self._config = config
        self._app = FastAPI(
            title=config.app_name,
            version="1.0.0",
            description="LLM Chat Auth Service",
            lifespan=self.lifespan
        )
        if config.cors.enabled:
            self._app.add_middleware(
                CORSMiddleware,
                allow_origins=config.cors.origins,
                allow_credentials=config.cors.credentials,
                allow_methods=config.cors.methods,
                allow_headers=config.cors.headers
            )

        for router in routers:
            self._app.include_router(router)

    async def lifespan(self, app: FastAPI) -> AsyncGenerator:
        """
        Создание схемы БД при запуске приложения.

        :param app: Приложение FastAPI.
        :return: None.
        """
        PWDContext.setup(
            self._config.password_hash.schemes,
            self._config.password_hash.bcrypt_rounds
        )
        DBSession.setup(
            self._config.db.database_url,
            self._config.db.schema
        )
        async with DBSession.engine().begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
        await DBSession.close()

    @property
    def app(self) -> FastAPI:
        return self._app

    @property
    def settings(self) -> Settings:
        return self._config
