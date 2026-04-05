from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from auth_service.app.api.deps import AuthUseCaseDep, UserDataDep
from auth_service.app.core.config import settings
from auth_service.app.schemas import auth as auth_schemas
from auth_service.app.schemas.user import UserPublic
from auth_service.app.consts.user_role import UserRole
from auth_service.app.schemas.error_detail import Detail


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post(
    "/register",
    response_model=auth_schemas.RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создание нового пользователя",
    responses={
        status.HTTP_409_CONFLICT: {
            "model": Detail
        }
    }
)
async def register(
        user_data: auth_schemas.RegisterRequest,
        usecase: AuthUseCaseDep,
):
    """
    Регистрация нового пользователя.

    :param user_data: Данные для регистрации.
    :param usecase: Usecase для работы с аутентификацией.

    :return: Данные нового пользователя.
    """
    data: UserPublic = await usecase.register(
        user_data.email,
        user_data.password,
        UserRole.user
    )
    return auth_schemas.RegisterResponse(
        user_id=str(data.id),
        email=data.email,
        role=data.role
    )


@router.post(
    "/login",
    response_model=auth_schemas.LoginResponse,
    summary="Вход пользователя (OAuth2 compatible)",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": Detail
        }
    }
)
async def login(
        data: Annotated[OAuth2PasswordRequestForm, Depends()],
        usecase: AuthUseCaseDep,
):
    """
    Вход пользователя (OAuth2 совместимый).

    :param data: Данные для входа.
    :param usecase: Usecase для работы с аутентификацией.

    :return: Access и refresh токены.
    """
    access, refresh = await usecase.login(
        data.username,
        data.password,
        settings.jwt
    )
    return auth_schemas.LoginResponse(
        access_token=access,
        refresh_token=refresh,
        token_type=settings.jwt.token_type,
        expires_in=settings.jwt.access_expire_seconds,
        refresh_expires_in=settings.jwt.refresh_expire_seconds
    )


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Профиль текущего пользователя",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": Detail
        }
    }
)
async def get_me(
        user_data: UserDataDep,
        usecase: AuthUseCaseDep,
) -> UserPublic:
    """
    Возвращает профиль текущего аутентифицированного пользователя.

    :param user_data: Данные из токена.
    :param usecase: Usecase для работы с аутентификацией.

    :return: Данные пользователя.
    """
    return await usecase.me(user_data.user_id)


@router.post(
    "/refresh",
    response_model=auth_schemas.RefreshTokenResponse,
    summary="Обновление access токена",
    description="Генерирует новый access токен по валидному refresh токену.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": Detail
        }
    }
)
async def refresh_token(
        data: auth_schemas.RefreshTokenRequest,
        usecase: AuthUseCaseDep,
) -> auth_schemas.RefreshTokenResponse:
    """
    Обновляет access токен по refresh токену.

    :param data: Запрос с refresh токеном.
    :param usecase: Usecase для работы с аутентификацией.

    :return: Новый access токен.
    """
    new_access_token = await usecase.refresh_token(
        refresh_token=data.refresh_token,
        jwt_config=settings.jwt,
    )

    return auth_schemas.RefreshTokenResponse(
        access_token=new_access_token,
        expires_in=settings.jwt.access_expire_seconds,
        token_type=settings.jwt.token_type
    )
