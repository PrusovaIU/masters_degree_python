from typing import Annotated

from fastapi import APIRouter, Query

from chat_api_service.app.api.deps.db import ConversationRepoDep
from chat_api_service.app.api.deps.jwt import UserDataDep
from chat_api_service.app.schemas.conversation import (
    ConversationListResponse,
    ConversationResponse, PaginationMeta,
)


router_chat = APIRouter(prefix="/chat", tags=["chat"])


@router_chat.get(
    "/conversations",
    response_model=ConversationListResponse,
    summary="Список диалогов пользователя",
    description="""
    Возвращает список диалогов текущего пользователя.

    Поддерживает пагинацию через параметры `limit` и `offset`.
    Диалоги отсортированы по дате последнего обновления (сначала новые).
    """,
)
async def list_conversations(
        current_user: UserDataDep,
        conversation_repo: ConversationRepoDep,
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
        offset: Annotated[int, Query(ge=0)] = 0,
) -> ConversationListResponse:
    """
    Получение списка диалогов пользователя.

    :param current_user: Аутентифицированный пользователь.
    :param conversation_repo: Репозиторий диалогов.
    :param limit: Количество элементов на странице.
    :param offset: Смещение для пагинации.
    :return: Список диалогов с метаданными пагинации.
    """
    user_id = str(current_user.user_id)

    conversations, total = await conversation_repo.list_by_user(
        user_id=user_id,
        limit=limit,
        offset=offset,
    )
    conversation_responses = [
        ConversationResponse.model_validate(conv, from_attributes=True)
        for conv in conversations
    ]

    return ConversationListResponse(
        conversations=conversation_responses,
        pagination=PaginationMeta(
            limit=limit,
            offset=offset,
            total=total
        )
    )


