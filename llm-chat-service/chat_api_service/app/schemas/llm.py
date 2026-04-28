from pydantic import BaseModel, Field

from chat_api_service.app.schemas.llm_tasks import LLMTaskStatusSchema


class CeleryTaskResponse(BaseModel):
    """
    Статус задачи обработки LLM-запроса.
    """
    result: LLMTaskStatusSchema | None = Field(
        default=None,
        description="Результат обработки"
    )
    status: str = Field(
        description="Статус задачи"
    )
    traceback: str | None = Field(
        default=None,
        description="Трассировка исключения (если есть)"
    )
