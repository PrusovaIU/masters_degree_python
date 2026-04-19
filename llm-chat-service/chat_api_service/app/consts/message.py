from enum import Enum


class MessageStatus(str, Enum):
    """
    Статусы сообщения
    """
    SENT = "sent"              # Сообщение отправлено пользователем
    PROCESSING = "processing"  # Обрабатывается
    DELIVERED = "delivered"    # Доставлено получателю
    READ = "read"              # Прочитано пользователем
    FAILED = "failed"          # Ошибка обработки


# Валидные переходы между статусами:
VALID_TRANSITIONS = {
    MessageStatus.SENT: [MessageStatus.PROCESSING, MessageStatus.FAILED],
    MessageStatus.PROCESSING: [MessageStatus.DELIVERED, MessageStatus.FAILED],
    MessageStatus.DELIVERED: [MessageStatus.READ],
    MessageStatus.READ: [],
    MessageStatus.FAILED: [],
}


class SenderType(Enum):
    """
    Тип отправителя сообщения
    """
    USER = "user"
    ASSISTANT = "assistant"
