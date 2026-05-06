from pydantic import BaseModel, Field

from libs.consts.llm_tasks import LLMTasksStatus


class LLMTaskStatusSchema(BaseModel):
    status: LLMTasksStatus = Field(description="Статус задачи")
    message_id: str = Field(description="ID сообщения")
    response_id: str | None = Field(default=None, description="ID ответа")
    task_id: str | None = Field(
        default=None,
        description="ID задачи обработки"
    )
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
    error_type: str | None = Field(
        default=None,
        description="Тип ошибки"
    )
    error: str | None = Field(
        default=None,
        description="Описание ошибки"
    )

    def to_dict(self):
        """Сериализация в словарь без None полей"""
        return self.model_dump(exclude_none=True)


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
