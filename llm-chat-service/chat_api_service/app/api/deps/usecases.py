from typing import Annotated

from chat_api_service.app.usecases.chat.history import ChatHistoryUsecase
from chat_api_service.app.api.deps.db import ConversationRepoDep, MessagesRepoDep
from fastapi import Depends


def chat_history_usecase(
        conversation_repo: ConversationRepoDep,
        message_repo: MessagesRepoDep,
):
    """
    Создание экземпляра класса ChatHistoryUsecase.

    :param conversation_repo: Репозиторий для работы с диалогами.
    :param message_repo: Репозиторий для работы с сообщениями.
    :return: Экземпляр класса ChatHistoryUsecase.
    """
    return ChatHistoryUsecase(
        conversation_repo,
        message_repo
    )


ChatHistoryUsecaseDep = Annotated[
    ChatHistoryUsecase,
    Depends(chat_history_usecase)
]
