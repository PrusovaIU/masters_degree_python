from uuid import UUID

from chat_api_service.app.core.exceptions.base import AppException


class TaskNotFound(AppException):
    def __init__(self, message: str, task_id: UUID):
        super().__init__(message, task_id=task_id)
