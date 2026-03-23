from pydantic import BaseModel, Field


class Pagination(BaseModel):
    """Пагинация"""
    limit: int = Field(ge=1, description="Количество элементов на странице")
    total: int = Field(ge=0, description="Общее количество элементов")
