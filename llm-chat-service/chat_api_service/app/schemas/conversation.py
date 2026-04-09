from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from chat_api_service.app.consts.message import MessageStatus
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

    before: datetime | None = Field(
        default=None,
        description="Получить сообщения старше указанной даты"
    )

    after: datetime | None = Field(
        default=None,
        description="Получить сообщения новее указанной даты"
    )

    status: list[MessageStatus] | None = Field(
        default=None,
        description="Фильтр по статусам сообщений"
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
    next_cursor: str | None = Field(
        default=None,
        description="Курсор для загрузки следующей страницы (ISO datetime)"
    )
    prev_cursor: str | None = Field(
        default=None,
        description="Курсор для загрузки предыдущей страницы (ISO datetime)"
    )


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
