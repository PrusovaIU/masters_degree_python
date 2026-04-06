from enum import Enum


class LLMTasksStatus(str, Enum):
    RATE_LIMITED = "rate_limited"
    ALREADY_PROCESSED = "already_processed"
    PROCESSING = "processing"
    CACHED = "cached"
