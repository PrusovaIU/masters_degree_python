from web_service.app.usecases.auth import AuthUsecase
from fastapi import Depends
from typing import Annotated


def auth_usecase() -> AuthUsecase:
    return AuthUsecase()


AuthUsecaseDep = Annotated[AuthUsecase, Depends(auth_usecase)]
