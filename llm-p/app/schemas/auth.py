from pydantic import BaseModel, EmailStr, Field


class _BaseUserRequest(BaseModel):
    email: EmailStr = Field(description="Email пользователя")
    password: str = Field(
        pattern=r"\w{8,100}$",
        description="Пароль (минимум 8 символов)"
    )


class RegisterRequest(_BaseUserRequest):
    """Схема запроса на регистрацию."""
    pass


class LoginRequest(_BaseUserRequest):
    """Схема запроса на авторизацию."""
    pass


class TokenResponse(BaseModel):
    """Схема ответа с токеном доступа."""
    access_token: str = Field(description="JWT токен доступа")
    token_type: str = Field(default="bearer", description="Тип токена")
