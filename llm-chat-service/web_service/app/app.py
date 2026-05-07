from collections.abc import AsyncGenerator

from web_service.app.core.config import Settings
from loguru import logger
from fastapi import FastAPI, Request, status
from starlette.middleware.cors import CORSMiddleware
from web_service.app.api import routers
from web_service.app.core.security import AuthCookieMiddleware
from fastapi.responses import RedirectResponse
from web_service.app.infra.rabbitmq import RabbitMQClient


class App:
    def __init__(self, config: Settings):
        self._config = config
        if config.logs.file_path:
            logger.add(
                config.logs.file_path,
                level=config.logs.level,
                rotation=config.logs.rotation
            )
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
        self._app.add_middleware(AuthCookieMiddleware)

        for router in routers:
            self._app.include_router(router)
        self._app.add_api_route("/", self.root)

        self._rabbitmq_client = RabbitMQClient(
            self._config.rabbitmq.url
        )

    async def lifespan(self, app: FastAPI) -> AsyncGenerator:
        await self._rabbitmq_client.connect()
        app.state.access_token_cookie_name = (
            self.settings.auth_cookie.access_token_cookie_name
        )
        app.state.rabbitmq_client = self._rabbitmq_client
        app.state.settings = self._config
        yield
        await self._rabbitmq_client.close()

    @property
    def app(self) -> FastAPI:
        return self._app

    @property
    def settings(self) -> Settings:
        return self._config

    @staticmethod
    async def root(request: Request):
        return RedirectResponse(
            "/chat",
            status_code=status.HTTP_302_FOUND
        )
