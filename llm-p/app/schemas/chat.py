from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .pagination import Pagination


class ChatRequest(BaseModel):
    """Схема запроса к чату."""
    prompt: str = Field(
        min_length=1,
        description="Текст запроса пользователя"
    )
    system: str | None = Field(
        default=None,
        description="Необязательная системная инструкция для модели"
    )
    max_history: int = Field(
        default=10,
        ge=0,
        le=50,
        description="Количество предыдущих сообщений из истории "
                    "для контекста (0-50)"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Параметр креативности модели "
                    "(0.0 - детерминировано, 2.0 - максимально креативно)"
    )


class ChatResponse(BaseModel):
    """Схема ответа чата."""
    answer: str = Field(description="Ответ модели на запрос пользователя")


class DeleteChatHistoryResponse(BaseModel):
    """Схема ответа на запрос удаления истории чата."""
    deleted_messages_amount: int = Field(
        ge=0,
        description="Количество удаленных сообщений"
    )


class ChatMessageResponse(BaseModel):
    """Схема для сообщения чата."""
    id: int = Field(description="ID сообщения")
    user_id: int = Field(description="ID пользователя")
    role: str = Field(description="Роль пользователя")
    content: str = Field(description="Текст сообщения")
    created_at: datetime = Field(description="Дата и время создания сообщения")

    model_config = ConfigDict(from_attributes=True)


class ChatHistoryResponse(BaseModel):
    pagination: Pagination = Field(description="Пагинация")
    data: list[ChatMessageResponse] = Field(description="История чата")
