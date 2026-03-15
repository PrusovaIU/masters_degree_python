from pydantic import BaseModel, Field


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
