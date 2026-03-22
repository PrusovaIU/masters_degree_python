from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserPublic(BaseModel):
    """Публичная схема пользователя для ответов API."""
    id: int = Field(description="ID пользователя")
    email: EmailStr = Field(description="Email пользователя")
    role: str = Field(description="Роль пользователя")
    created_at: datetime = Field(description="Дата создания пользователя")

    model_config = {
        "from_attributes": True
    }


@dataclass
class UserData:
    """Данные о пользователе, необходимые для работы с LLM."""
    user_id: int
    user_role: str
