from fastapi import APIRouter, HTTPException, status

from app.schemas.chat import ChatRequest, ChatResponse, DeleteChatHistoryResponse
from deps import UserDataDependency, ChatUsecaseDependency, UserIdDependency
from app.core.errors.openrouter_client import OpenRouterClientException
from app.db.models.chat_message import ChatMessage

chat_router = APIRouter(prefix="/chat", tags=["chat"])


@chat_router.post(
    "",
    response_model=ChatResponse,
    description="Отправить сообщение в чат и получить ответ от LLM."
)
async def send_message(
        chat_request: ChatRequest,
        user_data: UserDataDependency,
        chat_usecase: ChatUsecaseDependency
):
    """
    Отправить сообщение в чат и получить ответ от LLM.

    :param chat_request: Запрос на отправку сообщения.
    :param user_data: Данные текущего пользователя.
    :param chat_usecase: UseCase для работы с чатом.

    :return: Ответ от LLM.
    """
    try:
        answer = await chat_usecase.ask(
            user_data.user_id,
            user_data.user_role,
            chat_request.prompt,
            chat_request.system,
            chat_request.max_history,
            chat_request.temperature
        )
    except OpenRouterClientException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error accessing OpenRouter. Try later."
        )
    return ChatResponse(answer=answer)


@chat_router.get(
    "/history",
    response_model=list[ChatMessage],
    description="Получить историю сообщений текущего пользователя."
)
async def get_chat_history(
        user_id: UserIdDependency,
        chat_usecase: ChatUsecaseDependency,
        limit: int = 10
):
    """
    Получить историю сообщений текущего пользователя.

    :param user_id: ID текущего пользователя.
    :param chat_usecase: UseCase для работы с чатом.
    :param limit: Максимальное количество сообщений для возврата.

    :return: Список сообщений.
    """
    return await chat_usecase.history(user_id, limit)


@chat_router.delete(
    "/history",
    response_model=DeleteChatHistoryResponse,
    description="Очистить всю историю сообщений текущего пользователя."
)
async def clear_chat_history(
        user_id: UserIdDependency,
        chat_usecase: ChatUsecaseDependency
):
    """
    Очистить всю историю сообщений текущего пользователя.

    :param user_id: ID текущего пользователя.
    :param chat_usecase: UseCase для работы с чатом.

    :return: Количество удаленных сообщений.
    """
    return await chat_usecase.clear_history(user_id)
