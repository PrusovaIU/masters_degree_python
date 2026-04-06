from pydantic import BaseModel, Field


class AccessTokenData(BaseModel):
    """Данные токена"""
    sub: str = Field(description="ID пользователя")
    exp: int = Field(description="Время истечения токена")
    iat: int = Field(description="Время создания токена")
    token_type: str = Field(description="Тип токена")
    role: str = Field(description="Роль пользователя")
