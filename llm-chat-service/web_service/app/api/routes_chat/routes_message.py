from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from web_service.app.api.deps.current_user import AccessTokenDep
from web_service.app.api.deps.usecases import ChatUsecaseDep
from web_service.app.core.exceptions import chat_api_client as errors
from libs.schemas.message import MessageResponse

router_messages = APIRouter(prefix="/message")

@router_messages.get(
    "/{message_id}",
    response_model=MessageResponse,
    include_in_schema=False
)
async def get_message(
        access_token: AccessTokenDep,
        message_id: UUID,
        usecase: ChatUsecaseDep,
):
    """
    Получение сообщения.

    :param access_token: Access токен.
    :param message_id: Идентификатор сообщения.
    :param usecase: Usecase для работы с сообщениями.
    :return: Данные сообщения.
    """
    try:
        return await usecase.get_message(access_token, message_id)
    except errors.AccessException as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(err)
        )
    except errors.MessageNotFoundException as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err)
        )
