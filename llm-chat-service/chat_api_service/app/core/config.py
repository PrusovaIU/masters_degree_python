from functools import lru_cache

from chat_api_service.app.schemas.config import Settings


@lru_cache
def get_settings() -> Settings:
    """
    Кэшированный фабричный метод для получения настроек.
    Использует lru_cache для предотвращения повторного чтения .env файла.
    """
    return Settings()


# Глобальный экземпляр настроек для удобного импорта
settings = get_settings()
