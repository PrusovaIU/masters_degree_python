from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_serializer


# Unix epoch time
_UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


class TokenData(BaseModel):
    """Модель данных токена"""
    sub: str = Field(description="Пользователя ID")
    role: str = Field(description="Роль пользователя")
    exp: datetime = Field(description="Время истечения токена")
    iat: datetime = Field(description="Время создания токена")
    type: str = Field(description="Тип токена")
    payload: dict = Field(description="Дополнительные данные")

    @field_serializer("exp", "iat")
    def serialize_datetime(self, value: datetime) -> int:
        """Сериализация даты и время в количества секунд с начала эпохи"""
        total = (value - _UNIX_EPOCH).total_seconds()
        return int(total)

