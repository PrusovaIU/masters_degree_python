from chat_api_service.app.core.exceptions.base import AppException


class ChatHistoryException(AppException):
    """Базовое исключение для ошибок истории чата."""
    pass


class InvalidPaginationParams(ChatHistoryException):
    """
    Некорректные параметры пагинации.

    :param message: Сообщение об ошибке.
    :param provided_limit: Переданное значение limit.
    :param provided_offset: Переданное значение offset.
    :param allowed_range: Допустимый диапазон для limit.
    """

    def __init__(
            self,
            message: str,
            provided_limit: int | None = None,
            provided_offset: int | None = None,
            allowed_range: tuple[int, int] | None = None,
            before: str | None = None,
            after: str | None = None,
    ):
        super().__init__(
            message,
            provided_limit=provided_limit,
            provided_offset=provided_offset,
            allowed_range=allowed_range,
            before=before,
            after=after,
        )
        self._provided_limit = provided_limit
        self._provided_offset = provided_offset
        self._allowed_range = allowed_range
        self._before = before
        self._after = after
