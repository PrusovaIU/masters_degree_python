from app.schemas.error_detail import Detail

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
    def title(self) -> str:
        """
        :return: Заголовок исключения.
        """
        return self._title

    @property
    def message(self) -> str:
        """
        :return: Сообщение исключения.
        """
        return self._message

    @property
    def detail(self) -> Detail:
        return Detail(title=self.title, message=self.message)


class AppException(BaseAppException):
    def __init__(self, message: str | Exception):
        super().__init__(message)
