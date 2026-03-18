from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from .deps import AuthUsecaseDependency, AUTH_HEADERS, UserIdDependency
from app.consts.roles import Roles
from app.core.errors import usecase_auth as errors


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserPublic,
    description="Регистрация нового пользователя."
)
async def register(
        user_data: RegisterRequest,
        auth_usecase: AuthUsecaseDependency
):
    """
    Регистрация нового пользователя.

    :param user_data: Данные для регистрации.
    :param auth_usecase: Usecase для работы с аутентификацией.

    :return: Данные созданного пользователя.
    """
    try:
        user: UserPublic = await auth_usecase.register(
            email=user_data.email,
            password=user_data.password,
            role=Roles.USER
        )
    except errors.UserAlreadyExistsError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=err.message
        )
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    description="Вход в систему (OAuth2 совместимый)."
)
async def login(
        data: Annotated[OAuth2PasswordRequestForm, Depends()],
        auth_usecase: AuthUsecaseDependency
):
    """
    Вход в систему (OAuth2 совместимый).

    :param data: Данные для входа.
    :param auth_usecase: Usecase для работы с аутентификацией.

    :return: Токен доступа.
    """
    try:
        access_token: str = await auth_usecase.login(
            email=data.username,
            password=data.password
        )
    except errors.InvalidCredentialsError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=err.message,
            headers=AUTH_HEADERS
        )
    return TokenResponse(access_token=access_token)


@router.get(
    "/me",
    response_model=UserPublic,
    description="Получить информацию о текущем пользователе."
)
async def get_my_profile(
        user_id: UserIdDependency,
        auth_usecase: AuthUsecaseDependency
):
    """
    Получить информацию о текущем пользователе.

    :param user_id: ID текущего пользователя.
    :param auth_usecase: Usecase для работы с аутентификацией.

    :return: Данные текущего пользователя.
    """
    try:
        user = await auth_usecase.get_profile(user_id)
    except errors.UserNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=err.message
        )
    return user
