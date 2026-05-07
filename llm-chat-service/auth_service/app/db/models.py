from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from auth_service.app.consts.user_role import UserRole
from auth_service.app.db.base import AbstractBase


class User(AbstractBase):
    """
    Модель таблицы с пользователями.
    """
    __tablename__ = "user"

    email: Mapped[str] = mapped_column(
        String(256),
        unique=True,
        nullable=False,
        index=True,
        doc="Email пользователя (уникальный, используется для логина)",
    )

    password_hash: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        doc="Хеш пароля",
    )

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role_enum", create_type=False),
        nullable=False,
        doc="Роль пользователя",
    )

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, email={self.email!r}, "
            f"role={self.role.value})"
        )
