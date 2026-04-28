from uuid import UUID

from httpx import HTTPStatusError, TimeoutException
from fastapi import status

from web_service.app.core.utils.httpx_client import BaseClient, error_handler_decorator
from libs.schemas import conversation as schemas
from libs.schemas.pagination import PaginationRequest
from loguru import logger
from web_service.app.core.exceptions import chat_api_client as errors


class ChatAPIServiceClient(BaseClient):
    """Клиент для взаимодействия с сервисом chat_api."""

    @error_handler_decorator(
        errors.ListConversationsException,
        "Ошибка получения списка диалогов"
    )
    async def list_conversations(
            self,
            access_token: str,
            limit: int,
            offset: int
    ) -> schemas.ConversationListResponse:
        """
        Список диалогов пользователя.

        :param access_token: Токен доступа пользователя.
        :param limit: Количество диалогов на странице.
        :param offset: Смещение для пагинации.
        :return: Список диалогов пользователя.

        :raise ListConversationsException: В случае ошибки получения списка
            диалогов.
        """
        data = PaginationRequest(
            limit=limit,
            offset=offset
        ).model_dump(exclude_unset=True)
        async with self._get_client(access_token) as client:
            resp = await client.post(
                "/conversation/all",
                json=data
            )
            resp.raise_for_status()
            return schemas.ConversationListResponse(**resp.json())

    async def create_conversation(
            self,
            access_token: str,
            title: str
    ) -> schemas.ConversationCreateResponse:
        """
        Создание нового диалога.

        :param access_token: Токен доступа пользователя.
        :param title: Название диалога.

        :return: Созданный диалог.

        :raise CreateConversationException: В случае ошибки создания диалога.
        """
        data = schemas.ConversationCreateRequest(title=title).model_dump()
        try:
            async with self._get_client(access_token) as client:
                resp = await client.post(
                    "/conversation/",
                    json=data
                )
                resp.raise_for_status()
                return schemas.ConversationCreateResponse(**resp.json())
        except HTTPStatusError as err:
            logger.error(
                f"Ошибка создания диалога \"{title}\": {err.response.text} "
                f"(status_code={err.response.status_code})"
            )
            raise errors.CreateConversationException(
                err.response.text,
                conversation_title=title
            )
        except TimeoutException:
            logger.error(f"Ошибка создания диалога \"{title}\": timeout error")
            raise errors.CreateConversationException(
                "timeout error", title
            )
        except Exception as err:
            logger.error(
                f"Ошибка создания диалога \"{title}\": "
                f"{err} ({err.__class__.__name__})"
            )
            raise errors.CreateConversationException(
                "Не удалось создать диалог", title
            )

    async def get_conversation_history(
            self,
            access_token: str,
            conversation_id: UUID,
            limit: int = 20,
            offset: int = 0
    ) -> schemas.ConversationHistoryResponse:
        """
        История сообщений в диалоге.

        :param access_token: Токен доступа пользователя.
        :param conversation_id: Идентификатор диалога.
        :param limit: Количество сообщений на странице.
        :param offset: Смещение для пагинации.

        :return: История сообщений в диалоге.

        :raise ConversationAccessException: Если доступ к диалогу запрещен.
        :raise ConversationHistoryException: В случае ошибки получения истории.
        """
        try:
            async with self._get_client(access_token) as client:
                resp = await client.post(
                    "/conversation/history",
                    params={"conversation_id": str(conversation_id)},
                    json=PaginationRequest(limit=limit,
                                           offset=offset).model_dump(
                        exclude_unset=True)
                )
                resp.raise_for_status()
                return schemas.ConversationHistoryResponse(**resp.json())
        except HTTPStatusError as err:
            if err.response.status_code == status.HTTP_403_FORBIDDEN:
                logger.error(
                    f"Доступ к диалогу \"{conversation_id}\" запрещен"
                )
                raise errors.ConversationAccessException(
                    "Доступ запрещен",
                    conversation_id=conversation_id
                )
            else:
                logger.error(
                    f"Ошибка получения истории диалога: {err.response.text} "
                    f"(status_code={err.response.status_code}"
                )
                raise errors.ConversationHistoryException(
                    err.response.text,
                    conversation_id=conversation_id
                )
        except Exception as err:
            logger.error(
                f"Ошибка получения истории диалога: "
                f"{err} ({err.__class__.__name__})"
            )
            raise errors.ConversationHistoryException(
                "Не удалось получить историю диалога",
                conversation_id=conversation_id
            )


