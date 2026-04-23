from typing import Annotated

from fastapi import APIRouter, Query, status

from chat_api_service.app.api.deps.db import ConversationRepoDep
from chat_api_service.app.api.deps.jwt import UserDataDep
from chat_api_service.app.schemas import conversation
from chat_api_service.app.db.models import Conversation


router_chat = APIRouter(prefix="/conversation", tags=["chat"])


@router_chat.get(
    "/all",
    response_model=conversation.ConversationListResponse,
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
) -> conversation.ConversationListResponse:
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
        conversation.ConversationResponse.model_validate(
            conv,
            from_attributes=True
        )
        for conv in conversations
    ]

    return conversation.ConversationListResponse(
        conversations=conversation_responses,
        pagination=conversation.PaginationMeta(
            limit=limit,
            offset=offset,
            total=total
        )
    )


@router_chat.post(
    "/",
    response_model=conversation.ConversationCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового диалога",
    description="Создание нового диалога"
)
async def create_conversation(
        current_user: UserDataDep,
        conversation_repo: ConversationRepoDep,
        conversation_data: conversation.ConversationCreateRequest
):
    user_id = str(current_user.user_id)
    conv_data: Conversation = await conversation_repo.create(
        user_id,
        conversation_data.title
    )
    return conversation.ConversationCreateResponse(
        id=conv_data.id,
        title=conv_data.title,
        created_at=conv_data.created_at
    )
