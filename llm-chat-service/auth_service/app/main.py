from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth_service.app.api import routers
from auth_service.app.core.config import settings
from auth_service.app.db.base import Base
from auth_service.app.db.session import DBSession


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Создание схемы БД при запуске приложения.

    :param app: Приложение FastAPI.
    :return: None.
    """
    DBSession.setup(settings.db.database_url, settings.db.schema)
    async with DBSession.engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await DBSession.close()


def create_app() -> FastAPI:
    """
    Создание экземпляра FastAPI приложения.
    """
    new_app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="OpenRouter API",
        lifespan=lifespan
    )

    if settings.cors.enabled:
        new_app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors.origins,
            allow_credentials=settings.cors.credentials,
            allow_methods=settings.cors.methods,
            allow_headers=settings.cors.headers
        )

    for router in routers:
        new_app.include_router(router)

    return new_app


app = create_app()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
