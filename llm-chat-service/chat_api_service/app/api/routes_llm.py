from typing import Annotated

from fastapi import APIRouter, status, Header
from chat_api_service.app.schemas.llm import LLMQueryResponse, LLMQueryRequest
from .deps.jwt import UserDataDep
from .deps.rate_limit import RateLimitDep
from .deps.db import MessagesRepoDep
from chat_api_service.app.usecases.chat.new_message import NewMessageUsecase


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
        custom_idem_key: Annotated[
            str | None,
            Header(None, alias="X-Idempotency-Key")
        ],
        msg_repo: MessagesRepoDep
) -> LLMQueryResponse:
    """
    Запуск асинхронного запроса к LLM.

    :param user_message_data: Данные запроса.
    :param current_user: Аутентифицированный пользователь.
    :param custom_idem_key: Опциональный ключ идемпотентности от клиента.
    :param rate_limit_ok: Результат проверки rate limiting.
    :param msg_repo: Репозиторий сообщений.

    :return: Статус сообщения.
    """
    user_id = str(current_user.user_id)
    usecase = NewMessageUsecase(
        msg_repo,
        user_id,
        user_message_data,
        custom_idem_key
    )
    response = await usecase.execute()
    return response