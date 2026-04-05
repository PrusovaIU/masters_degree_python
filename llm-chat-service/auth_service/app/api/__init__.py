from .router_auth import router as auth_router
from .router_health import health_router


routers = [auth_router, health_router]


__all__ = [
    "auth_router",
    "health_router",
    "routers"
]
