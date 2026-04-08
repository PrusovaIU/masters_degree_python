from pydantic import BaseModel, Field


class Detail(BaseModel):
    title: str = Field(description="Заголовок ошибки")
    message: str = Field(description="Сообщение об ошибке")
    metadata: dict | None = Field(
        default=None,
        description="Дополнительные данные"
    )


class ErrorDetail(BaseModel):
    detail: Detail = Field(description="Описание ошибки")