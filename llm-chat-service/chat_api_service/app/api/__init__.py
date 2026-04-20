from .routes_chat import router_chat
from .routes_llm import router_llm
from .router_health import router_health


routers = [
    router_chat,
    router_llm,
    router_health
]
