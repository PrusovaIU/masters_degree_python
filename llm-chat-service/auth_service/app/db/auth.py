from pydantic import BaseModel, Field, EmailStr


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

    user_id: str = Field(description="ID созданного пользователя")
    email: EmailStr = Field(
        description="Email зарегистрированного пользователя"
    )


class TokenResponse(BaseModel):
    """
    Схема ответа с токеном доступа.

    Возвращается при успешном логине или регистрации.
    """
    access_token: str = Field(description="JWT access токен")
    token_type: str = Field(
        default="bearer",
        description="Тип токена",
    )
    expires_in: int = Field(
        description="Время жизни токена в секундах",
        ge=0
    )


class RefreshTokenResponse(BaseModel):
    """
    Схема ответа с парой токенов (access + refresh).
    """
    access_token: str = Field(description="JWT access токен")
    refresh_token: str = Field(description="JWT refresh токен")
    token_type: str = Field(
        default="bearer",
        description="Тип токена"
    )
    expires_in: int = Field(description="Время жизни access токена в секундах")
    refresh_expires_in: int = Field(
        description="Время жизни refresh токена в секундах"
    )


class LoginResponse(RefreshTokenResponse):
    """
    Схема ответа для эндпоинта логина.
    """
    pass


class TokenRefreshRequest(BaseModel):
    """
    Схема запроса для обновления токена.

    Используется в POST /auth/refresh
    """

    refresh_token: str = Field(
        ...,
        description="Валидный refresh токен",
    )
