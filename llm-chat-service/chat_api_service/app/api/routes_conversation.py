from uuid import UUID

from fastapi import APIRouter, status, HTTPException

import libs.schemas.pagination
from chat_api_service.app.api.deps.jwt import UserDataDep
from libs.schemas import conversation
from chat_api_service.app.db.models import Conversation
from chat_api_service.app.api.deps.usecases import ConversationUsecaseDep
from chat_api_service.app.schemas.message import MessageResponse, \
    MessageStatusUpdate
from libs.schemas.pagination import PaginationRequest
from chat_api_service.app.core.exceptions import conversation as errs
from chat_api_service.app.core.exceptions import message as msg_errs
from libs.schemas.error_detail import Detail
from fastapi.encoders import jsonable_encoder
from .deps.usecases import MessageUsecaseDep


router_conversation = APIRouter(prefix="/conversation", tags=["chat"])


@router_conversation.post(
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
        conversations_usecase: ConversationUsecaseDep,
        pagination: PaginationRequest
) -> conversation.ConversationListResponse:
    """
    Получение списка диалогов пользователя.

    :param current_user: Аутентифицированный пользователь.
    :param conversations_usecase: Usecase работы с диалогами.
    :param pagination: Параметры пагинации.
    :return: Список диалогов с метаданными пагинации.
    """
    user_id = str(current_user.user_id)

    conversations, total = await conversations_usecase.list_conversations(
        user_id, pagination.limit, pagination.offset
    )

    return conversation.ConversationListResponse(
        conversations=conversations,
        pagination=libs.schemas.pagination.PaginationMeta(
            limit=pagination.limit,
            offset=pagination.offset,
            total=total
        )
    )


@router_conversation.post(
    "/",
    response_model=conversation.ConversationCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового диалога",
    description="Создание нового диалога"
)
async def create_conversation(
        current_user: UserDataDep,
        conversation_usecase: ConversationUsecaseDep,
        conversation_data: conversation.ConversationCreateRequest
):
    user_id = str(current_user.user_id)
    conv_data: Conversation = await conversation_usecase.create_conversation(
        user_id, conversation_data.title
    )
    return conversation.ConversationCreateResponse(
        id=conv_data.id,
        title=conv_data.title,
        created_at=conv_data.created_at
    )


@router_conversation.post(
    "/history",
    response_model=conversation.ConversationHistoryResponse,
    summary="История сообщений в диалоге",
    description="История сообщений в диалоге",
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": Detail
        },
        status.HTTP_404_NOT_FOUND: {
            "model": Detail
        },
    }
)
async def get_history(
        conversation_id: UUID,
        current_user: UserDataDep,
        chat_history_usecase: ConversationUsecaseDep,
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
    except errs.ConversationAccessDenied as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=jsonable_encoder(err.detail)
        )
    return history


@router_conversation.patch(
    "/messages/{message_id}/status",
    response_model=MessageResponse,
    summary="Изменение статуса сообщения",
    description="Изменение статуса сообщения",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": Detail
        },
        status.HTTP_403_FORBIDDEN: {
            "model": Detail
        },
        status.HTTP_404_NOT_FOUND: {
            "model": Detail
        },
    }
)
async def update_message_status(
        message_id: UUID,
        new_status: MessageStatusUpdate,
        current_user: UserDataDep,
        msg_usecase: MessageUsecaseDep
) -> MessageResponse:
    """
    Обновление статуса сообщения.

    :param message_id: Идентификатор сообщения.
    :param new_status: Новый статус сообщения.
    :param current_user: Текущий пользователь.
    :param msg_usecase: Usecase сообщений.
    :return: Обновленное сообщение.
    """
    try:
        updated_message = await msg_usecase.status_update(
            message_id,
            str(current_user.user_id),
            new_status.status
        )
    except msg_errs.InvalidMessageStatus as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err.detail_jsonable_encoder
        )
    except errs.ConversationAccessDenied as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=err.detail_jsonable_encoder
        )
    except msg_errs.MessageNotFound as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=err.detail_jsonable_encoder
        )
    return MessageResponse.model_validate(
        updated_message,
        from_attributes=True
    )
