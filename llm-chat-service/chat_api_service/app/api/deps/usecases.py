from typing import Annotated

from chat_api_service.app.db.models import Conversation
from chat_api_service.app.usecases.chat.conversation import ConversationUsecase
from chat_api_service.app.api.deps.db import ConversationRepoDep, MessagesRepoDep
from fastapi import Depends


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


ConversationUsecaseDep = Annotated[
    ConversationUsecase,
    Depends(conversation_usecase)
]
