class BaseAppException(Exception):
    """
    Базовый класс исключений.

    :param title: Заголовок исключения.
    :param message: Сообщение исключения.
    """
    def __init__(
            self,
            message: str | Exception,
            title: str | None = None
    ):
        self._title = title if title else self.__class__.__name__
        self._message = str(message)

    def __str__(self):
        return f"{self._title}: {self._message}"

    @property
    def title(self):
        return self._title

    @property
    def message(self):
        return self._message

    def detail(self) -> dict:
        return {
            "detail": self.__str__()
        }


class AppException(BaseAppException):
    def __init__(self, message: str | Exception):
        super().__init__(message)
