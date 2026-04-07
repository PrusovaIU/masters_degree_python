from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

from chat_api_service.app.consts.message import MessageStatus, SenderType


class MessageCreate(BaseModel):
    """Модель для создания сообщения"""
    sender_type: SenderType | str
    content: str = Field(min_length=1, max_length=65536)
    status: MessageStatus | str
    metadata: dict | None = Field(default=None)


class MessageStatusUpdate(BaseModel):
    """Модель для обновления статуса сообщения"""
    status: MessageStatus
