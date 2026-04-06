from pydantic import BaseModel, Field
from chat_api_service.app.consts.llm_tasks import LLMTasksStatus
from uuid import UUID
from chat_api_service.app.consts.message import SenderType


class LLMTaskStatusSchema(BaseModel):
    status: LLMTasksStatus = Field(description="Статус задачи")
    message_id: UUID = Field(description="ID сообщения")
    retry_after: int | None = Field(
        default=None,
        description="Время до следующей попытки в секундах"
    )
    content: str | None = Field(
        default=None,
        description="Содержимое сообщения"
    )
    note: str | None = Field(
        default=None,
        description="Примечание"
    )

    def to_dict(self):
        """Сериализация в словарь без None полей"""
        return self.model_dump(exclude_none=True)


class MessageSchema(BaseModel):
    """Модель сообщения для LLM"""
    role: SenderType = Field(description="Роль отправителя")
    content: str = Field(description="Контекст сообщения")
