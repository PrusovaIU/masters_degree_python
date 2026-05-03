from web_service.app.usecases.auth import AuthUsecase
from fastapi import Depends
from typing import Annotated
from .services import AuthClientDep
from web_service.app.core.config import settings


def auth_usecase(auth_client: AuthClientDep) -> AuthUsecase:
    return AuthUsecase(auth_client, settings)


AuthUsecaseDep = Annotated[AuthUsecase, Depends(auth_usecase)]
