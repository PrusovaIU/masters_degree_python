from enum import Enum


class LLMTasksStatus(str, Enum):
    RATE_LIMITED = "rate_limited"  # Слишком много запросов
    ALREADY_PROCESSED = "already_processed"  # Уже обработано
    PROCESSING = "processing"  # В обработке
    CACHED = "cached"  # В кэше
    SUCCESS = "success"  # Успешно
    ERROR = "error"  # Ошибка
