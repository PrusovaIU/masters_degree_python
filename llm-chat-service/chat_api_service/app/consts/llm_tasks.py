from enum import Enum
from typing import Self


class LLMTasksStatus(str, Enum):
    RATE_LIMITED = "rate_limited"  # Слишком много запросов
    ALREADY_PROCESSED = "already_processed"  # Уже обработано
    PROCESSING = "processing"  # В обработке
    CACHED = "cached"  # В кэше
    SUCCESS = "success"  # Успешно
    ERROR = "error"  # Ошибка
    QUEUED = "queued"  # В очереди
    UNKNOWN = "unknown"

    @staticmethod
    def get_status(status: str):
        """
        Получение статуса по строке.
        """
        for item in LLMTasksStatus:
            if item.value == status:
                return item
        return LLMTasksStatus.UNKNOWN
