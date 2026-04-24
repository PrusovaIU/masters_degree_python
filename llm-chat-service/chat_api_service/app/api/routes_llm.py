from typing import Annotated

from fastapi import APIRouter, status, Header, HTTPException
from chat_api_service.app.schemas.llm import LLMQueryResponse, LLMQueryRequest
from .deps.jwt import UserDataDep
from .deps.rate_limit import RateLimitDep
from .deps.db import MessagesRepoDep, ConversationRepoDep
from chat_api_service.app.usecases.chat.new_message import NewMessageUsecase
from chat_api_service.app.schemas.llm import LLMStatusResponse
from chat_api_service.app.core.exceptions.conversation import (
    ConversationNotFound, ConversationAccessDenied)
from .deps.usecases import MessageUsecaseDep


router_llm = APIRouter(prefix="/chat/llm", tags=["llm"])


@router_llm.post(
    "/query",
    response_model=LLMQueryResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Запуск асинхронного запроса к LLM",
    description="Отправление сообщения пользователя на обработку LLM"
)
async def query_llm(
        user_message_data: LLMQueryRequest,
        current_user: UserDataDep,
        rate_limit_ok: RateLimitDep,
        msg_repo: MessagesRepoDep,
        conversation_repo: ConversationRepoDep,
        custom_idem_key: Annotated[
            str | None,
            Header(alias="X-Idempotency-Key")
        ] = None
) -> LLMQueryResponse:
    """
    Запуск асинхронного запроса к LLM.

    :param user_message_data: Данные запроса.
    :param current_user: Аутентифицированный пользователь.
    :param custom_idem_key: Опциональный ключ идемпотентности от клиента.
    :param rate_limit_ok: Результат проверки rate limiting.
    :param msg_repo: Репозиторий сообщений.
    :param conversation_repo: Репозиторий диалогов.

    :return: Статус сообщения.
    """
    user_id = str(current_user.user_id)
    usecase = NewMessageUsecase(
        msg_repo,
        conversation_repo,
        user_id,
        user_message_data,
        custom_idem_key
    )
    try:
        response: LLMQueryResponse = await usecase.execute()
    except ConversationNotFound as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=err.detail
        )
    except ConversationAccessDenied as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=err.detail
        )
    return response


@router_llm.get(
    "/status/{task_id}",
    response_model=LLMStatusResponse,
    summary="Получение статуса задачи LLM"
)
async def get_llm_task_status(
        task_id: str,
        current_user: UserDataDep,
        msg_usecase: MessageUsecaseDep,
) -> LLMStatusResponse:
    """
    Получение статуса задачи LLM.

    :param task_id: UUID задачи Celery.
    :param current_user: Аутентифицированный пользователь.
    :param msg_usecase: Usecase сообщений.

    :return: Статус задачи.
    """
    user_id = str(current_user.user_id)
    try:
        response: LLMStatusResponse = await msg_usecase.get_by_task_id(
            task_id, user_id
        )
    except ConversationNotFound as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=err.detail
        )
    except ConversationAccessDenied as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=err.detail
        )
    return response
