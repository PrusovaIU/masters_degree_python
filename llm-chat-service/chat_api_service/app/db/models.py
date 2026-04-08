from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import (
    String, Text, DateTime, Enum, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from chat_api_service.app.consts.message import MessageStatus, SenderType, VALID_TRANSITIONS
from .base import Base
from chat_api_service.app.core.exceptions.message import InvalidMessageStatus


class Conversation(Base):
    """
    Модель диалога (чата).
    """
    __tablename__ = "conversation"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
    )
    user_id: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        index=True,
        comment="Идентификатор пользователя из Auth Service"
    )
    title: Mapped[str] = mapped_column(
        String(256),
        nullable=True,
        comment="Заголовок диалога (автогенерируемый или пользовательский)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (f"<Conversation(id={self.id}, user_id={self.user_id}, "
                f"title='{self.title}')>")


class Message(Base):
    """
    Модель сообщения в диалоге.
    """
    __tablename__ = "message"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
    )
    conversation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(Conversation.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender_type: Mapped[SenderType] = mapped_column(
        Enum(SenderType, name="sender_type_enum"),
        nullable=False,
        comment="Тип отправителя"
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Текст сообщения"
    )
    status: Mapped[MessageStatus] = mapped_column(
        Enum(MessageStatus, name="message_status_enum"),
        nullable=False,
        index=True,
        comment="Статус доставки/обработки"
    )
    idempotency_key: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        comment="Уникальный ключ для идемпотентных запросов"
    )
    llm_task_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="ID задачи Celery для асинхронного LLM-запроса"
    )
    metadata_json: Mapped[dict | None] = mapped_column(
        comment="Доп. метаданные (например, токены, модель, стоимость)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Время доставки/получения ответа"
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Время прочтения"
    )

    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="messages",
    )

    def __repr__(self) -> str:
        return (f"<Message(id={self.id}, conv={self.conversation_id}, "
                f"sender={self.sender_type}, status={self.status})>")

    def update_status(self, new_status: MessageStatus) -> None:
        """
        Обновление статуса.

        :param new_status: Новый статус сообщения

        :raises ValueError: Если переход в недопустимое состояние.
        """
        if new_status not in VALID_TRANSITIONS.get(self.status, []):
            raise InvalidMessageStatus(
                f"Невалидных переход статуса",
                old_status=self.status,
                new_status=new_status
            )
        self.status = new_status
        now = datetime.now(timezone.utc)
        if new_status == MessageStatus.DELIVERED and not self.delivered_at:
            self.delivered_at = now
        elif new_status == MessageStatus.READ and not self.read_at:
            self.read_at = now
