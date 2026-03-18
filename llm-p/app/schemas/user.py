from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from dataclasses import dataclass


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
