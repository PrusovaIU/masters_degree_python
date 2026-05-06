from uuid import UUID

from pydantic import BaseModel, Field


class RabbitMQMessageStatus(BaseModel):
    """Схема для публикации информации о статусе сообщения в RabbitMQ."""
    message_id: UUID = Field(
        description="Идентификатор обработанного сообщения"
    )
    answer_id: UUID = Field(
        description="Идентификатор ответного сообщения"
    )
    conversation_id: UUID = Field(
        description="Идентификатор диалога"
    )
    user_id: str = Field(
        description="Идентификатор пользователя"
    )
