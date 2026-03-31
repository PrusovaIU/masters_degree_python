from datetime import datetime, timezone, timedelta

from pydantic import BaseModel, Field, field_serializer
from auth_service.app.consts.token_type import TokenType
from typing import Self


# Unix epoch time
_UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


class TokenData(BaseModel):
    """Модель данных токена"""
    sub: str = Field(description="Пользователя ID")
    exp: datetime = Field(description="Время истечения токена")
    iat: datetime = Field(description="Время создания токена")
    token_type: TokenType = Field(
        default=TokenType.not_set,
        description="Тип токена",
        alias="type"
    )

    @field_serializer("exp", "iat")
    def serialize_datetime(self, value: datetime) -> int:
        """Сериализация даты и время в количества секунд с начала эпохи"""
        total = (value - _UNIX_EPOCH).total_seconds()
        return int(total)

    @classmethod
    def new(
            cls,
            sub: str,
            exp_delta: timedelta,
            token_type: TokenType
    ) -> Self:
        """
        Создание нового экземпляра класса.
        """
        now = datetime.now(timezone.utc)
        exp = now + exp_delta
        return cls(
            sub=sub,
            exp=exp,
            iat=now,
            type=token_type
        )



class AccessTokenData(TokenData):
    """Модель данных access токена"""
    type: str = Field(default=TokenType.access, description="Тип токена")
    payload: dict | None = Field(description="Дополнительные данные")
    role: str = Field(
        default="unknown",
        description="Роль пользователя"
    )

    @classmethod
    def new(
            cls,
            sub: str,
            role: str,
            exp_delta: timedelta,
            payload: dict | None = None
    ) -> Self:
        ins = super().new(sub, exp_delta, TokenType.access)
        ins.role = role
        if payload:
            ins.payload = payload
        return ins


class RefreshTokenData(TokenData):
    """Модель данных refresh токена"""
    type: str = Field(default=TokenType.refresh, description="Тип токена")

    @classmethod
    def new(
            cls,
            sub: str,
            exp_delta: timedelta
    ) -> Self:
        return super().new(sub, exp_delta, TokenType.refresh)
