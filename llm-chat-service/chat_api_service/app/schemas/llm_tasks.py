from pydantic import BaseModel, Field

from libs.consts.message import SenderType


class MessageSchema(BaseModel):
    """Модель сообщения для LLM"""
    role: SenderType | str = Field(description="Роль отправителя")
    content: str = Field(description="Контекст сообщения")
