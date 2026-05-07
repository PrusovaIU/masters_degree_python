from pydantic import BaseModel, Field

from libs.consts.message import MessageStatus, SenderType


class MessageCreate(BaseModel):
    """Модель для создания сообщения"""
    sender_type: SenderType | str
    content: str = Field(min_length=1, max_length=65536)
    status: MessageStatus | str
    metadata: dict | None = Field(default=None)
