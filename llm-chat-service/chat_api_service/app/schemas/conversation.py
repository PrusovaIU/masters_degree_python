from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from .message import MessageResponse


class ConversationHistoryParams(BaseModel):
    """Параметры для запроса истории сообщений."""
    limit: int | None = Field(
        default=None,
        ge=1,
        le=100,
        description="Количество сообщений на странице"
    )
    offset: int | None = Field(
        default=0,
        ge=0,
        description="Смещение для пагинации"
    )

    @model_validator(mode="after")
    def validate_mutual_exclusion(self) -> Self:
        """before и after не могут быть заданы одновременно"""
        if self.before and self.after:
            raise ValueError(
                "Параметры 'before' и 'after' не могут быть использованы "
                "одновременно"
            )

        return self


class PaginationMeta(BaseModel):
    """Метаданные пагинации в ответе."""
    limit: int = Field(description="Запрошенное количество элементов")
    offset: int = Field(description="Запрошенное смещение")
    total: int = Field(description="Общее количество элементов")


class ConversationHistoryResponse(BaseModel):
    """Ответ с историей сообщений диалога."""
    conversation_id: UUID = Field(description="UUID диалога")
    conversation_title: str | None = Field(
        default=None,
        description="Заголовок диалога"
    )
    messages: list[MessageResponse] = Field(  # type: ignore  # noqa: F821
        description="Список сообщений в хронологическом порядке"
    )
    pagination: PaginationMeta = Field(description="Метаданные пагинации")

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Ответ с данными диалога."""
    id: UUID = Field(description="UUID диалога")
    user_id: str = Field(description="ID владельца диалога")
    title: str | None = Field(default=None, description="Заголовок диалога")
    created_at: datetime = Field(description="Время создания")
    updated_at: datetime = Field(description="Время последнего обновления")

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """Ответ со списком диалогов."""
    conversations: list[ConversationResponse] = Field(
        description="Список диалогов"
    )
    pagination: PaginationMeta = Field(description="Метаданные пагинации")


class ConversationCreateRequest(BaseModel):
    """Запрос на создание диалога."""
    title: str = Field(description="Заголовок диалога")


class ConversationCreateResponse(BaseModel):
    """Ответ на создание диалога."""
    id: UUID = Field(description="UUID созданного диалога")
    title: str = Field(description="Заголовок диалога")
    created_at: datetime = Field(description="Время создания диалога")
