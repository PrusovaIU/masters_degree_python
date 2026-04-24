from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, status, HTTPException

import chat_api_service.app.schemas.pagination
from chat_api_service.app.api.deps.db import ConversationRepoDep
from chat_api_service.app.api.deps.jwt import UserDataDep
from chat_api_service.app.schemas import conversation
from chat_api_service.app.db.models import Conversation
from chat_api_service.app.api.deps.usecases import ChatHistoryUsecaseDep
from chat_api_service.app.schemas.pagination import PaginationRequest
from chat_api_service.app.core.exceptions import conversation as errs
from libs.schemas.error_detail import Detail
from fastapi.encoders import jsonable_encoder


router_chat = APIRouter(prefix="/conversation", tags=["chat"])


@router_chat.post(
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
        pagination: PaginationRequest
) -> conversation.ConversationListResponse:
    """
    Получение списка диалогов пользователя.

    :param current_user: Аутентифицированный пользователь.
    :param conversation_repo: Репозиторий диалогов.
    :param pagination: Параметры пагинации.
    :return: Список диалогов с метаданными пагинации.
    """
    user_id = str(current_user.user_id)

    conversations, total = await conversation_repo.list_by_user(
        user_id=user_id,
        limit=pagination.limit,
        offset=pagination.offset,
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
        pagination=chat_api_service.app.schemas.pagination.PaginationMeta(
            limit=pagination.limit,
            offset=pagination.offset,
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


@router_chat.post(
    "/history",
    response_model=conversation.ConversationHistoryResponse,
    summary="История сообщений в диалоге",
    description="История сообщений в диалоге",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": Detail
        }
    }
)
async def get_history(
        conversation_id: UUID,
        current_user: UserDataDep,
        chat_history_usecase: ChatHistoryUsecaseDep,
        pagination_data: PaginationRequest,
) -> conversation.ConversationHistoryResponse:
    """
    Получение истории сообщений в диалоге.

    :param conversation_id: ID диалога.
    :param current_user: Текущий пользователь.
    :param chat_history_usecase: Usecase истории сообщений.
    :param pagination_data: Данные пагинации.
    :return: История сообщений.
    """
    user_id = str(current_user.user_id)
    try:
        history: conversation.ConversationHistoryResponse = \
            await chat_history_usecase.get_history(
                conversation_id,
                user_id,
                pagination_data.limit,
                pagination_data.offset
            )
    except errs.ConversationNotFound as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=jsonable_encoder(err.detail)
        )
    return history
