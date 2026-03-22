from pydantic import BaseModel, Field


class HealthCheck(BaseModel):
    """
    Модель ответа на запрос проверки работоспособности сервиса.
    """
    status: str = Field(description="Статус сервиса")
    environment: str = Field(description="Окружение")
