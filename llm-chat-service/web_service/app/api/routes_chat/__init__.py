from fastapi import APIRouter, status
from fastapi.responses import HTMLResponse, RedirectResponse

from .routes_conversation import router_conversation
from .routes_message import router_messages

router_chat = APIRouter(prefix="/chat")
router_chat.include_router(router_conversation)
router_chat.include_router(router_messages)


@router_chat.get(
    "/",
    response_class=HTMLResponse,
    include_in_schema=False
)
def chat():
    return RedirectResponse(
        url="/chat/conversation/all",
        status_code=status.HTTP_302_FOUND
    )

