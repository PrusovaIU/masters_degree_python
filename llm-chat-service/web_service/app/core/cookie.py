from fastapi import Response, Request

from libs.schemas.user import UserPublic
from web_service.app.schemas.config import AuthCookieSettings, CookieSettings, Settings
from web_service.app.schemas.user import User
from .exceptions.cookie import CookieUnfoundException
from loguru import logger


def set_access_token_cookie(
        response: Response,
        settings: AuthCookieSettings,
        access_token: str,
        expires_in: int | None
) -> None:
    """
    Установка cookie с access токеном.

    :param response: Ответ на запрос;
    :param settings: Настройки cookie;
    :param access_token: Access токен;
    :param expires_in: Время жизни токена;
    :return: None
    """
    response.set_cookie(
        key=settings.access_token_cookie_name,
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_same_site,
        max_age=expires_in
    )


def set_refresh_token_cookie(
        response: Response,
        settings: AuthCookieSettings,
        refresh_token: str,
        expires_in: int | None
) -> None:
    """
    Установка cookie с refresh токеном.

    :param response: Ответ на запрос;
    :param settings: Настройки cookie;
    :param refresh_token: Refresh токен;
    :param expires_in: Время жизни токена;
    :return: None
    """
    response.set_cookie(
        key=settings.refresh_token_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_same_site,
        max_age=expires_in
    )


def set_auth_cookies(
        response: Response,
        settings: AuthCookieSettings,
        access_token: str,
        access_expires: int | None,
        refresh_token: str,
        refresh_expires: int | None
) -> None:
    """
    Установка cookie с токенами авторизации.

    :param response: Response - объект ответа FastAPI;
    :param settings: Настройки cookie.
    :param access_token: access токен;
    :param refresh_token: refresh токен;
    :param access_expires: время жизни access токена;
    :param refresh_expires: время жизни refresh токена.
    :returns: None.
    """
    set_access_token_cookie(
        response,
        settings,
        access_token,
        access_expires
    )
    set_refresh_token_cookie(
        response,
        settings,
        refresh_token,
        refresh_expires
    )


def set_user_cookie(
        response: Response,
        settings: CookieSettings,
        user_data: UserPublic,
        access_expires: int | None
) -> None:
    """
    Установка cookie с данными пользователя. Cookie устанавливаются на время
    жизни access токена.

    :param response: Response - объект ответа FastAPI.
    :param settings: Настройки cookie.
    :param user_data: Данные пользователя.
    :param access_expires: Время жизни токена.
    :return: None
    """
    response.set_cookie(
        key=settings.user_email_cookie_name,
        value=user_data.email,
        max_age=access_expires
    )
    response.set_cookie(
        key=settings.user_role_cookie_name,
        value=user_data.role,
        max_age=access_expires
    )
    response.set_cookie(
        key=settings.user_id_cookie_name,
        value=str(user_data.id),
        max_age=access_expires
    )


def get_user_cookie(
        request: Request,
        cookie_settings: CookieSettings
) -> User:
    """
    Получение данных пользователя из cookie.

    :param request: Запрос FastAPI.
    :param cookie_settings: Настройки cookie.
    :return: Данные пользователя.

    :raises CookieUnfoundException: Cookie не найден.
    """
    try:
        user_id: str = request.cookies[cookie_settings.user_id_cookie_name]
        email: str = request.cookies[cookie_settings.user_email_cookie_name]
        role: str = request.cookies[cookie_settings.user_role_cookie_name]
        return User(id=user_id, email=email, role=role)
    except KeyError as err:
        logger.warning(f"Cookie не найден: {err}")
        raise CookieUnfoundException(
            "Cookie не найден",
            cookie_name=str(err)
        )



def clear_auth_cookies(
        response: Response,
        settings: Settings
) -> None:
    """
    Очистка cookie авторизации.

    :param response: Response - объект ответа FastAPI.
    :param settings: Настройки приложения.
    :returns: None.
    """
    for cookie_name in settings.cookies:
        response.delete_cookie(cookie_name, path="/")
