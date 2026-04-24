from pydantic import BaseModel, Field


class PaginationRequest(BaseModel):
    """Параметры пагинации"""
    limit: int | None = Field(
        default=20,
        ge=1,
        le=100,
        description="Количество сообщений на странице"
    )
    offset: int | None = Field(
        default=0,
        ge=0,
        description="Смещение для пагинации"
    )


class PaginationMeta(BaseModel):
    """Метаданные пагинации в ответе."""
    limit: int = Field(description="Запрошенное количество элементов")
    offset: int = Field(description="Запрошенное смещение")
    total: int = Field(description="Общее количество элементов")
