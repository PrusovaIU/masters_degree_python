from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

from chat_api_service.app.consts.message import MessageStatus, SenderType


class MessageCreate(BaseModel):
    sender_type: SenderType
    content: str = Field(min_length=1, max_length=65536)
    status: Optional[MessageStatus] = None
    metadata: Optional[dict] = None


class MessageStatusUpdate(BaseModel):
    status: MessageStatus
