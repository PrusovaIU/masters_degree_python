from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserPublic(BaseModel):
    """Публичная схема пользователя для ответов API."""
    id: int = Field(description="ID пользователя")
    email: EmailStr = Field(description="Email пользователя")
    password_hash: str = Field(description="Хеш пароля пользователя")
    role: str = Field(description="Роль пользователя")
    created_at: datetime = Field(description="Дата создания пользователя")
    updated_at: datetime = Field(description="Дата обновления пользователя")

    model_config = ConfigDict(from_attributes=True)


@dataclass
class TokenUserData:
    """Данные пользователя из JWT токена."""
    user_id: int
    user_role: str
