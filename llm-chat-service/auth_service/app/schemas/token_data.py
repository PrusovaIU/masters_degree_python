from datetime import datetime, timezone, timedelta

from pydantic import BaseModel, Field, field_serializer, field_validator
from auth_service.app.consts.token_type import TokenType
from typing import Self, ClassVar





class TokenData(BaseModel):
    """Модель данных токена"""
    _TOKEN_TYPE: ClassVar[TokenType] = TokenType.not_set
    _target_classes: ClassVar[dict[TokenType, type[Self]]] = {}
    # Unix epoch time
    _UNIX_EPOCH: ClassVar[datetime] = datetime(
        1970, 1, 1, tzinfo=timezone.utc
    )

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._target_classes[cls._TOKEN_TYPE] = cls


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
        total = (value - self._UNIX_EPOCH).total_seconds()
        return int(total)

    @field_validator("exp", "iat", mode="before")
    @classmethod
    def validate_datetime(cls, value: datetime |  int) -> datetime:
        """Валидация даты и времени"""
        if isinstance(value, datetime):
            return value
        elif isinstance(value, int):
            return datetime.fromtimestamp(value, tz=timezone.utc)
        else:
            raise ValueError(
                "Неверный формат даты: ожидается datetime или int"
            )

    @classmethod
    def new(
            cls,
            sub: str,
            exp: timedelta | int,
            token_type: TokenType,
            **kwargs
    ) -> Self:
        """
        Создание нового экземпляра класса.

        :param sub: Идентификатор пользователя.

        :param exp: Время истечения токена:
            - timedelta: интервал времени, в течении которого токен
                действителен.
            - int: количество секунд с начала эпохи, до точки истечения срока
                жизни токена.

        :param token_type: Тип токена.

        :param kwargs: Дополнительные параметры.

        :return: Новый экземпляр класса, соответствующий типу токена:
            - AccessTokenData для токенов типа access.
            - RefreshTokenData для токенов типа refresh.
        """
        now = datetime.now(timezone.utc)
        if isinstance(exp, timedelta):
            exp = now + exp
        try:
            target_class: type[Self] = cls._target_classes[token_type]
        except KeyError as err:
            raise SystemError(f"Неизвестный тип токена: {token_type}") from err
        return target_class(
            sub=sub,
            exp=exp,
            iat=now,
            type=token_type,
            **kwargs
        )


class AccessTokenData(TokenData):
    """Модель данных access токена"""
    _TOKEN_TYPE: ClassVar[TokenType] = TokenType.access
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
            exp: timedelta | int,
            payload: dict | None = None
    ) -> Self:
        ins = super().new(sub, exp, cls._TOKEN_TYPE, role=role)
        if payload:
            ins.payload = payload
        return ins


class RefreshTokenData(TokenData):
    """Модель данных refresh токена"""
    _TOKEN_TYPE: ClassVar[TokenType] = TokenType.refresh
    token_type: TokenType = Field(
        default=_TOKEN_TYPE,
        description="Тип токена",
        alias="type"
    )

    @classmethod
    def new(
            cls,
            sub: str,
            exp: timedelta | int,
            *kwargs
    ) -> Self:
        return super().new(sub, exp, cls._TOKEN_TYPE)
