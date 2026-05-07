from .routes_admin import router_admin
from .routes_auth import router_auth
from .routes_chat import router_chat

routers = [
    router_auth,
    router_chat,
    router_admin
]