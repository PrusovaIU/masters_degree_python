from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from libs.schemas.message import MessageResponse
from libs.schemas.pagination import PaginationMeta


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



class ConversationHistoryBeforeResponse(BaseModel):
    """
    Ответ с историей сообщений диалога до указанного сообщения.
    """
    messages: list[MessageResponse] = Field(description="Список сообщений")
    has_more: bool = Field(description="Флаг наличия еще сообщений")


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
