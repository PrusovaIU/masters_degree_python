from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from libs.consts.message import MessageStatus, SenderType


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

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
