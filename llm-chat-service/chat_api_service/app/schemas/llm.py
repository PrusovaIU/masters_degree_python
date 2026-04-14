from datetime import datetime
from chat_api_service.app.consts.llm_tasks import LLMTasksStatus
from uuid import UUID

from pydantic import BaseModel, Field


class LLMQueryRequest(BaseModel):
    """
    Запрос к LLM.

    Используется в POST /chat/llm/query
    """
    conversation_id: UUID = Field(description="UUID диалога")
    content: str = Field(
        min_length=1,
        max_length=65536,
        description="Текст сообщения пользователя"
    )
    temperature: float | None = Field(
        ge=0.0,
        le=2.0,
        description="Параметр креативности "
                    "(0.0 — детерминировано, 2.0 — максимально случайно)"
    )


class LLMQueryResponse(BaseModel):
    """
    Ответ на запрос к LLM.

    Возвращается сразу после постановки задачи в очередь.
    """
    message_id: UUID = Field(description="UUID созданного сообщения")

    task_id: str = Field(description="ID задачи Celery для отслеживания")

    status: LLMTasksStatus = Field(description="Текущий статус обработки")

    conversation_id: UUID = Field(description="UUID диалога")

    content: str | None = Field(
        default=None,
        description="Текст ответа (если кэширован)"
    )

    response_id: UUID | None = Field(
        default=None,
        description="UUID сообщения-ответа"
    )

    note: str | None = Field(
        default=None,
        description="Дополнительная информация"
    )

    class Config:
        from_attributes = True


class LLMStatusResponse(BaseModel):
    """
    Статус задачи обработки LLM-запроса.

    Используется в GET /chat/llm/status/{task_id}
    """
    task_id: str = Field(description="ID задачи Celery")
    status: LLMTasksStatus = Field(description="Текущий статус")

    message_id: UUID | None = Field(
        default=None,
        description="UUID сообщения-запроса"
    )

    conversation_id: UUID | None = Field(
        default=None,
        description="UUID диалога"
    )

    content: str | None = Field(
        default=None,
        description="Текст ответа LLM"
    )

    response_id: UUID | None = Field(
        default=None,
        description="UUID сообщения-ответа"
    )

    error: str | None = Field(
        default=None,
        description="Описание ошибки"
    )

    error_type: str | None = Field(
        default=None,
        description="Тип ошибки"
    )

    created_at: datetime | None = Field(
        default=None,
        description="Время создания задачи"
    )

    updated_at: datetime | None = Field(
        default=None,
        description="Время последнего обновления"
    )

    class Config:
        from_attributes = True
