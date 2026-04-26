from .routes_conversation import router_conversation
from .routes_llm import router_llm
from .router_health import router_health
from .routes_admin import router_admin


routers = [
    router_conversation,
    router_llm,
    router_admin,
    router_health
]
