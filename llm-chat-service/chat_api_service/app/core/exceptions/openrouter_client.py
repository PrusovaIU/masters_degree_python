"""Исключения для работы с клиентом OpenRouter."""
from .base import AppException


class OpenRouterClientException(AppException):
    """Базовое исключение для OpenRouterClient"""
    pass


class UnexpectedResponseException(OpenRouterClientException):
    """
    Исключение, пробрасываемое при получении ответа с неожиданным форматом.
    """
    pass


class TimeoutException(OpenRouterClientException):
    """Исключение, пробрасываемое при превышении таймаута запроса."""
    pass
