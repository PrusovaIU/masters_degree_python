from typing import Annotated

from fastapi import Depends
from auth_service.app.usecases.auth import AuthUseCase
from .db import UserRepoDep


def get_auth_uc(
        user_repo: UserRepoDep,
) -> AuthUseCase:
    """
    :param user_repo: Репозиторий для работы с таблицей пользователей.
    :return: Экземпляр AuthUseCase.
    """
    return AuthUseCase(user_repo=user_repo)


AuthUseCaseDep = Annotated[AuthUseCase, Depends(get_auth_uc)]
