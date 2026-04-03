from pydantic import BaseModel, Field, EmailStr, ConfigDict
from auth_service.app.consts.user_role import UserRole


class RegisterRequest(BaseModel):
    """
    Схема запроса для регистрации нового пользователя.
    """
    email: EmailStr = Field(
        max_length=256,
        description="Email пользователя",
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        examples=["user@example.com"]
    )

    password: str = Field(
        min_length=8,
        max_length=128,
        description="Пароль пользователя",
        examples=["P@ssw0rd!"]
    )


class RegisterResponse(BaseModel):
    """
    Схема ответа для эндпоинта регистрации.
    """
    model_config = ConfigDict(from_attributes=True)

    user_id: str = Field(description="ID созданного пользователя")
    email: EmailStr = Field(
        description="Email зарегистрированного пользователя"
    )
    role: str = Field(description="Роль пользователя")


class RefreshTokenRequest(BaseModel):
    """Схема запроса для обновления access токена."""
    refresh_token: str = Field(description="JWT refresh токен")


class RefreshTokenResponse(BaseModel):
    """Схема ответа с новым access токеном."""
    access_token: str = Field(description="JWT access токен")
    expires_in: int = Field(description="Время жизни access токена в секундах")
    token_type: str = Field(
        default="bearer",
        description="Тип токена"
    )


class LoginRequest(RegisterRequest):
    """Схема запроса для авторизации пользователя."""
    pass


class LoginResponse(RefreshTokenResponse):
    """
    Схема ответа с парой токенов (access + refresh).
    """
    refresh_token: str = Field(description="JWT refresh токен")
    refresh_expires_in: int = Field(
        description="Время жизни refresh токена в секундах"
    )
