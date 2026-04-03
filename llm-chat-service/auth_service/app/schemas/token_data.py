from datetime import datetime, timezone, timedelta

from pydantic import BaseModel, Field, field_serializer, field_validator, model_validator
from auth_service.app.consts.jwt_token import TokenType
from typing import Self, ClassVar
from functools import lru_cache


class TokenData(BaseModel):
    """Модель данных токена"""
    _TOKEN_TYPE: ClassVar[TokenType] = TokenType.not_set
    # Список классов для каждого типа токена:
    _target_classes: ClassVar[dict[TokenType, type[Self]]] = {}
    # Unix epoch time
    _UNIX_EPOCH: ClassVar[datetime] = datetime(
        1970, 1, 1, tzinfo=timezone.utc
    )

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._target_classes[cls._TOKEN_TYPE] = cls

    @classmethod
    def get_target_class(cls, token_type: TokenType) -> type[Self]:
        """
        Получение класса для указанного типа токена.

        :param token_type: Тип токена.
        :return: Класс, соответствующий типу токена.
        """
        try:
            return cls._target_classes[token_type]
        except KeyError as err:
            raise SystemError(
                f"Неподдерживаемый тип токена: {token_type}"
            ) from err

    sub: str = Field(description="Пользователя ID")
    exp: datetime = Field(description="Время истечения токена")
    iat: datetime = Field(description="Время создания токена")
    token_type: TokenType = Field(
        description="Тип токена",
        alias="type"
    )

    @field_validator("token_type", mode="before")
    @classmethod
    def set_default_token_type(cls, value: TokenType | None) -> TokenType:
        if value is None:
            return cls._TOKEN_TYPE
        return value

    @field_serializer("exp", "iat")
    def serialize_datetime(self, value: datetime) -> int:
        """Сериализация даты и время в количества секунд с начала эпохи"""
        total = (value - self._UNIX_EPOCH).total_seconds()
        return int(total)

    @field_serializer("token_type")
    def serialize_token_type(self, value: TokenType) -> str:
        """Сериализация типа токена"""
        return value.value

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
            exp: timedelta,
            token_type: TokenType,
            **kwargs
    ) -> Self:
        """
        Создание нового экземпляра класса.

        :param sub: Идентификатор пользователя.

        :param exp: Время жизни токена.

        :param token_type: Тип токена.

        :param kwargs: Дополнительные параметры.

        :return: Новый экземпляр класса, соответствующий типу токена:
            - AccessTokenData для токенов типа access.
            - RefreshTokenData для токенов типа refresh.
        """
        target_class = cls.get_target_class(token_type)
        now = datetime.now(timezone.utc)
        exp = now + exp
        return target_class(
            sub=sub,
            exp=exp,
            iat=now,
            type=token_type,
            **kwargs
        )

    @classmethod
    def from_token_data(cls, token_type: TokenType, **kwargs) -> Self:
        """
        Создание экземпляра класса из словаря параметров расшифрованного
        токена.

        :param token_type: Тип токена.
        :param kwargs: Параметры токена.
        :return: Новый экземпляр класса, соответствующий типу токена:
            - AccessTokenData для токенов типа access.
            - RefreshTokenData для токенов типа refresh.
        """
        target_class = cls.get_target_class(token_type)
        return target_class(**kwargs)


    def model_dump(self, **kwargs) -> dict:
        """
        Переопределение метода сериализации модели для использования алиасов
        по умолчанию.
        """
        return super().model_dump(**kwargs, by_alias=True)

    @classmethod
    @lru_cache(maxsize=16)
    def model_params_vnames(cls) -> list[str]:
        """
        :return: Список имен параметров модели для валидации.
        """
        names = []
        for name, field in cls.model_fields.items():
            names.append(
                field.alias or field.validation_alias or name
            )
        return names


class AccessTokenData(TokenData):
    """Модель данных access токена"""
    _TOKEN_TYPE: ClassVar[TokenType] = TokenType.access
    payload: dict | None = Field(
        description="Дополнительные данные",
        exclude_if=lambda v: v is None
    )
    role: str = Field(
        default="unknown",
        description="Роль пользователя"
    )

    _PAYLOAD_FIELD: ClassVar[str] = "payload"

    @model_validator(mode="before")
    @classmethod
    def validate(cls, values: dict) -> dict:
        """
        Валидатор модели, служащий для обработки динамических полей, которые
        не определены в схеме модели.

        Все поля, не входящие в список стандартных параметров модели,
        собираются в словарь и помещаются в поле payload.
        """
        model_parameters_names = cls.model_params_vnames()
        payload_parameters = {
            key: value for key, value in values.items()
            if key not in model_parameters_names
        }
        if payload_parameters:
            payload = values.get(cls._PAYLOAD_FIELD)
            if payload is None:
                payload = payload_parameters
            else:
                payload.update(payload_parameters)
            values[cls._PAYLOAD_FIELD] = payload
            for key in payload_parameters:
                values.pop(key)
        if cls._PAYLOAD_FIELD not in values:
            values[cls._PAYLOAD_FIELD] = None
        return values

    @classmethod
    def new(
            cls,
            sub: str,
            exp: timedelta,
            role: str,
            payload: dict | None = None
    ) -> Self:
        """
        Создание нового экземпляра класса AccessTokenData.

        :param sub: Идентификатор пользователя.
        :param exp: Время жизни токена.
        :param role: Роль пользователя.
        :param payload: Дополнительные данные.
        :return: Новый экземпляр класса AccessTokenData.
        """
        ins = super().new(
            sub, exp, cls._TOKEN_TYPE, role=role, payload=payload
        )
        return ins


class RefreshTokenData(TokenData):
    """Модель данных refresh токена"""
    _TOKEN_TYPE: ClassVar[TokenType] = TokenType.refresh

    @classmethod
    def new(
            cls,
            sub: str,
            exp: timedelta,
            **kwargs
    ) -> Self:
        """
        Создание нового экземпляра класса RefreshTokenData.

        :param sub: Идентификатор пользователя.
        :param exp: Время жизни токена.
        :param kwargs: Для совместимости.
        :return: None.
        """
        return super().new(sub, exp, cls._TOKEN_TYPE)
