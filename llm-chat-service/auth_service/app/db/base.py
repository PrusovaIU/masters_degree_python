from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех SQLAlchemy моделей."""
    pass


class AbstractBase(Base):
    """
    Абстрактный базовый класс с общими полями для всех моделей:
        - id: первичный ключ (UUID)
        - created_at: время создания
        - updated_at: время последнего обновления
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        doc="Время создания записи",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_onupdate=func.now(),
        doc="Время последнего обновления записи",
    )

    def to_dict(self, exclude: list[str] | None = None) -> dict[str, Any]:
        """
        Конвертация модели в словарь.

        :param exclude: Список полей для исключения из результата.
        :return: Словарь с данными модели.
        """
        exclude = exclude or []
        return {
            field.name: getattr(self, field.name)
            for field in self.__table__.columns
            if field.name not in exclude
        }
