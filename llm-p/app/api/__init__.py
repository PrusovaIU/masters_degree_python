from .routes_auth import auth_router
from .routes_chat import chat_router
from .routes_health import health_router

routers = (
    auth_router,
    chat_router,
    health_router
)

__all__ = [
    "routers"
]
