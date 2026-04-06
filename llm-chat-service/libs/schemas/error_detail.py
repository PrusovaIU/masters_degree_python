from pydantic import BaseModel, Field


class Detail(BaseModel):
    title: str = Field(description="Заголовок ошибки")
    message: str = Field(description="Сообщение об ошибке")


class ErrorDetail(BaseModel):
    detail: Detail = Field(description="Описание ошибки")