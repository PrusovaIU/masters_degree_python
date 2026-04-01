from datetime import datetime, timezone, timedelta

from pydantic import BaseModel, Field, field_serializer, field_validator
from auth_service.app.consts.token_type import TokenType
from typing import Self


# Unix epoch time
_UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


class TokenData(BaseModel):
    """Модель данных токена"""
    _TOKEN_TYPE = TokenType.not_set
    __classes: dict[TokenType, type[Self]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__classes[cls._TOKEN_TYPE] = cls


    sub: str = Field(description="Пользователя ID")
    exp: datetime = Field(description="Время истечения токена")
    iat: datetime = Field(description="Время создания токена")
    token_type: TokenType = Field(
        default=_TOKEN_TYPE,
        description="Тип токена",
        alias="type"
    )

    @field_serializer("exp", "iat")
    def serialize_datetime(self, value: datetime) -> int:
        """Сериализация даты и время в количества секунд с начала эпохи"""
        total = (value - _UNIX_EPOCH).total_seconds()
        return int(total)

    @field_validator("exp", "iat", mode="before")
    @classmethod
    def validate_datetime(cls, value: datetime |  int) -> datetime:
        """Валидация даты и времени"""
        if isinstance(value, datetime):
            return value
        elif isinstance(value, int):
            return _UNIX_EPOCH + timedelta(seconds=value)
        else:
            raise ValueError(
                "Неверный формат даты: ожидается datetime или int"
            )

    @classmethod
    def new(
            cls,
            sub: str,
            exp_delta: timedelta,
            token_type: TokenType,
            **kwargs
    ) -> Self:
        """
        Создание нового экземпляра класса.
        """
        now = datetime.now(timezone.utc)
        exp = now + exp_delta
        target_class: type[Self] = cls.__classes[token_type]
        return target_class(
            sub=sub,
            exp=exp,
            iat=now,
            type=token_type,
            **kwargs
        )


class AccessTokenData(TokenData):
    """Модель данных access токена"""
    _TOKEN_TYPE = TokenType.access
    token_type: TokenType = Field(
        default=_TOKEN_TYPE,
        description="Тип токена",
        alias="type"
    )
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
        ins = super().new(sub, exp_delta, cls._TOKEN_TYPE, role=role)
        if payload:
            ins.payload = payload
        return ins


class RefreshTokenData(TokenData):
    """Модель данных refresh токена"""
    _TOKEN_TYPE = TokenType.refresh
    token_type: TokenType = Field(
        default=_TOKEN_TYPE,
        description="Тип токена",
        alias="type"
    )

    @classmethod
    def new(
            cls,
            sub: str,
            exp_delta: timedelta
    ) -> Self:
        return super().new(sub, exp_delta, cls._TOKEN_TYPE)
