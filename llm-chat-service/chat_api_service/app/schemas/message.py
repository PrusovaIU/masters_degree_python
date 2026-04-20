from datetime import datetime

from pydantic import BaseModel, Field
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


class MessageResponse(BaseModel):
    """
    Схема ответа с сообщением.
    """
    id: UUID = Field(description="UUID сообщения")
    conversation_id: UUID = Field(description="UUID диалога")
    sender_type: SenderType = Field(description="Тип отправителя")
    content: str = Field(description="Текст сообщения")
    status: MessageStatus = Field(description="Статус сообщения")
    created_at: datetime = Field(description="Время создания")
    updated_at: datetime = Field(description="Время последнего обновления")
    delivered_at: datetime | None = Field(
        default=None,
        description="Время доставки/получения ответа"
    )
    read_at: datetime | None = Field(
        default=None,
        description="Время прочтения"
    )
    metadata: dict | None = Field(
        default=None,
        description="Дополнительные метаданные",
        alias="metadata_json"
    )

    class Config:
        from_attributes = True
        populate_by_name = True
