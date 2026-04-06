from typing import Any

from libs.schemas.error_detail import Detail
from fastapi import HTTPException, status


class BaseAppException(HTTPException):
    """
    Базовый класс исключений.

    :param error_code: Код исключения.
    :param message: Сообщение исключения.
    """
    def __init__(
            self,
            status_code: int,
            message: str,
            headers: dict[str, Any] | None = None,
            error_code: str | None = None
    ):
        self._error_code = error_code if error_code \
            else self.__class__.__name__
        self._message = str(message)
        super().__init__(
            status_code,
            self.error_detail.model_dump(),
            headers
        )

    def __str__(self):
        return f"{self._error_code}: {self._message}"

    @property
    def error_code(self) -> str:
        """
        :return: Заголовок исключения.
        """
        return self._error_code

    @property
    def message(self) -> str:
        """
        :return: Сообщение исключения.
        """
        return self._message

    @property
    def error_detail(self) -> Detail:
        return Detail(title=self.error_code, message=self.message)


class AppException(BaseAppException):
    @property
    def exc_status_code(self) -> int:
        return status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
            self,
            message: str,
            headers: dict[str, Any] | None = None,
    ):
        super().__init__(self.exc_status_code, message, headers)
