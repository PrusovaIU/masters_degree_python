from fastapi import status

from libs.base_exception import AppException


class UserAlreadyExistsError(AppException):
    """
    Ошибка, возникающая при попытке создать пользователя, который уже существует.
    """
    @property
    def exc_status_code(self) -> int:
        return status.HTTP_409_CONFLICT


class UserNotFoundError(AppException):
    """
    Ошибка, возникающая при попытке получить несуществующего пользователя.
    """
    @property
    def exc_status_code(self) -> int:
        return status.HTTP_404_NOT_FOUND


class GetUserError(AppException):
    """
    Ошибка, возникающая при попытке получить пользователя.
    """
    pass
