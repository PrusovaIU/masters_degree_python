from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.consts.roles import Roles
from app.db.base import Base


class User(Base):
    """Модель таблицы user для хранения информации о пользователях."""
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(256),
        unique=True,
        index=True,
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=Roles.user
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
