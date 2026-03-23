from dataclasses import dataclass


@dataclass
class Message:
    """
    Схема сообщения для LLM.
    """
    role: str
    content: str
