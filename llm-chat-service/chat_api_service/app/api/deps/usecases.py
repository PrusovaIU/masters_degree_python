from typing import Annotated

from fastapi import Depends

from chat_api_service.app.usecases.admin.tasks import TasksUsecase
from chat_api_service.app.usecases.chat.conversation import ConversationUsecase
from chat_api_service.app.usecases.chat.message import MessageUsecase

from .db import ConversationRepoDep, MessagesRepoDep


def conversation_usecase(
        conversation_repo: ConversationRepoDep,
        message_repo: MessagesRepoDep,
):
    """
    Создание экземпляра класса ChatHistoryUsecase.

    :param conversation_repo: Репозиторий для работы с диалогами.
    :param message_repo: Репозиторий для работы с сообщениями.
    :return: Экземпляр класса ChatHistoryUsecase.
    """
    return ConversationUsecase(
        conversation_repo,
        message_repo
    )


def message_usecase(
        message_repo: MessagesRepoDep,
        conversation_repo: ConversationRepoDep,
) -> MessageUsecase:
    """
    Создание экземпляра класса MessageUsecase.

    :param message_repo: Репозиторий для работы с сообщениями.
    :return: Экземпляр класса MessageUsecase.
    """
    return MessageUsecase(
        message_repo,
        conversation_repo
    )


def tasks_usecase() -> TasksUsecase:
    return TasksUsecase()


ConversationUsecaseDep = Annotated[
    ConversationUsecase,
    Depends(conversation_usecase)
]
MessageUsecaseDep = Annotated[
    MessageUsecase,
    Depends(message_usecase)
]
TasksUsecaseDep = Annotated[
    TasksUsecase,
    Depends(tasks_usecase)
]
