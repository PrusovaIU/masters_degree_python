from fastapi import APIRouter

from .routes_conversation import router_conversation

router_chat = APIRouter(prefix="/chat")
router_chat.include_router(router_conversation)
