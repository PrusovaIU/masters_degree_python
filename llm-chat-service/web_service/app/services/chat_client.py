from typing import Type
from uuid import UUID

from httpx import HTTPStatusError, TimeoutException
from fastapi import status

from web_service.app.core.utils.httpx_client import BaseClient, error_handler_decorator
from libs.schemas import conversation as conv_schemas
from libs.schemas.pagination import PaginationRequest
from loguru import logger
from web_service.app.core.exceptions import chat_api_client as errors
from libs.schemas.llm_query import LLMQueryRequest, LLMQueryResponse
from functools import wraps
from libs.schemas.message import MessageStatusUpdate
from libs.schemas.message import MessageResponse
from libs.schemas.llm import CeleryTaskResponse


def conv_error_handler(
        error_type: Type[errors.ChatApiClientException],
        title: str
):
    """
    Декоратор для обработки ошибок, связанных с диалогом.

    :param error_type: Тип пробрасываемого исключения.
    :param title: Заголовок для логирования.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, conversation_id: UUID, **kwargs):
            try:
                return await func(*args, conversation_id=conversation_id, **kwargs)
            except HTTPStatusError as err:
                match err.response.status_code:
                    case status.HTTP_403_FORBIDDEN:
                        logger.error(
                            f"Доступ к диалогу \"{conversation_id}\" запрещен"
                        )
                        raise errors.AccessException(
                            "Доступ запрещен",
                            conversation_id=conversation_id
                        )
                    case status.HTTP_404_NOT_FOUND:
                        logger.error(f"Диалог \"{conversation_id}\" не найден")
                        raise errors.ConversationNotFoundException(
                            "Диалог не найден",
                            conversation_id=conversation_id
                        )
                    case _:
                        logger.error(
                            f"{title}: {err.response.text} "
                            f"(status_code={err.response.status_code}"
                        )
                        raise error_type(
                            err.response.text,
                            conversation_id=conversation_id
                        )
            except TimeoutException:
                logger.error(f"{title}: timeout error")
                raise error_type(
                    "timeout error",
                    conversation_id=conversation_id
                )
            except Exception as err:
                logger.error(
                    f"{title}: {err} ({err.__class__.__name__})"
                )
                raise error_type(
                    title,
                    conversation_id=conversation_id
                )
        return wrapper
    return decorator


def msg_error_handler(
        error_type: Type[errors.MessageException],
        title: str
):
    """
    Декоратор для обработки ошибок, связанных с сообщением.

    :param error_type: Тип пробрасываемого исключения.
    :param title: Заголовок для логирования.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, message_id: UUID, **kwargs):
            try:
                return await func(*args, message_id=message_id, **kwargs)
            except HTTPStatusError as err:
                match err.response.status_code:
                    case status.HTTP_403_FORBIDDEN:
                        logger.error(
                            f"Доступ к сообщению \"{message_id}\" запрещен"
                        )
                        raise errors.AccessException(
                            "Доступ запрещен",
                            _id=message_id
                        )
                    case status.HTTP_404_NOT_FOUND:
                        logger.error(f"Сообщение \"{message_id}\" не найдено")
                        raise errors.MessageNotFoundException(
                            "Сообщение не найдено",
                            message_id=message_id
                        )
                    case _:
                        logger.error(
                            f"{title}: {err.response.text} "
                            f"(status_code={err.response.status_code}"
                        )
                        raise error_type(
                            err.response.text,
                            message_id=message_id
                        )
            except TimeoutException:
                logger.error(f"{title}: timeout error")
                raise error_type(
                    "timeout error",
                    message_id=message_id
                )
            except Exception as err:
                logger.error(
                    f"{title}: {err} ({err.__class__.__name__})"
                )
                raise error_type(
                    title,
                    message_id=message_id
                )
        return wrapper
    return decorator



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
    ) -> conv_schemas.ConversationListResponse:
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
            return conv_schemas.ConversationListResponse(**resp.json())

    async def create_conversation(
            self,
            access_token: str,
            title: str
    ) -> conv_schemas.ConversationCreateResponse:
        """
        Создание нового диалога.

        :param access_token: Токен доступа пользователя.
        :param title: Название диалога.

        :return: Созданный диалог.

        :raise CreateConversationException: В случае ошибки создания диалога.
        """
        data = conv_schemas.ConversationCreateRequest(title=title).model_dump()
        try:
            async with self._get_client(access_token) as client:
                resp = await client.post(
                    "/conversation/",
                    json=data
                )
                resp.raise_for_status()
                return conv_schemas.ConversationCreateResponse(**resp.json())
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

    @msg_error_handler(
        errors.ChangeMessageStatusException,
        "Ошибка изменения статуса сообщения"
    )
    async def update_message_status(
            self,
            access_token: str,
            message_id: UUID,
            new_status: str
    ) -> MessageResponse:
        """
        Изменение статуса сообщения.
        :param access_token: Токен доступа пользователя.
        :param message_id: Идентификатор сообщения.
        :param new_status: Новый статус сообщения.

        :return: Обновленное сообщение.
        """
        title = "Ошибка изменения статуса сообщения"
        async with self._get_client(access_token) as client:
            resp = await client.patch(
                f"/conversation/messages/{message_id}/status",
                json=MessageStatusUpdate(status=new_status).model_dump()
            )
            resp.raise_for_status()
            return MessageResponse(**resp.json())

    @conv_error_handler(
        errors.ConversationHistoryException,
        "Ошибка получения истории диалога"
    )
    async def get_conversation_history(
            self,
            access_token: str,
            conversation_id: UUID,
            limit: int = 20,
            offset: int = 0
    ) -> conv_schemas.ConversationHistoryResponse:
        """
        История сообщений в диалоге.

        :param access_token: Токен доступа пользователя.
        :param conversation_id: Идентификатор диалога.
        :param limit: Количество сообщений на странице.
        :param offset: Смещение для пагинации.

        :return: История сообщений в диалоге.

        :raise AccessException: Если доступ к диалогу запрещен.
        :raise ConversationNotFoundException: Если диалог не найден.
        :raise ConversationHistoryException: В случае ошибки получения истории.
        """
        async with self._get_client(access_token) as client:
            resp = await client.post(
                "/conversation/history",
                params={"conversation_id": str(conversation_id)},
                json=PaginationRequest(
                    limit=limit,
                    offset=offset
                ).model_dump(exclude_unset=True)
            )
            resp.raise_for_status()
            return conv_schemas.ConversationHistoryResponse(**resp.json())

    @conv_error_handler(
        errors.ConversationHistoryException,
        "Ошибка получения истории диалога"
    )
    async def conversation_history_before(
            self,
            access_token: str,
            conversation_id: UUID,
            before_message_id: UUID,
            limit: int = 20
    ) -> conv_schemas.ConversationHistoryBeforeResponse:
        """
        История сообщений в диалоге до определенного сообщения.

        :param access_token: Токен доступа пользователя.

        :param conversation_id: Идентификатор диалога.

        :param before_message_id: Идентификатор сообщения, до которого нужно
            получить историю.

        :param limit: Количество сообщений на странице.

        :return: История сообщений в диалоге.

        :raise AccessException: Если доступ к диалогу запрещен.
        :raise ConversationNotFoundException: Если диалог не найден.
        :raise ConversationHistoryException: В случае ошибки получения истории.
        """
        params = {
            "conversation_id": str(conversation_id),
            "before_message_id": str(before_message_id),
            "limit": limit
        }
        async with self._get_client(access_token) as client:
            resp = await client.get(
                "/conversation/history/before",
                params=params
            )
            resp.raise_for_status()
            return conv_schemas.ConversationHistoryBeforeResponse(
                **resp.json()
            )

    async def query_llm(
            self,
            access_token: str,
            conversation_id: UUID,
            content: str,
            temperature: float | None = 0.7,
            idempotency_key: str | None = None
    ) -> LLMQueryResponse:
        """
        Запрос к LLM.

        :param access_token: Токен доступа пользователя.
        :param conversation_id: Идентификатор диалога.
        :param content: Текст запроса.
        :param temperature: Температура генерации ответа.
        :param idempotency_key: Ключ идемпотентности запроса.

        :return: Ответ LLM.

        :raise ConversationAccessException: Если доступ к диалогу запрещен.
        :raise ConversationNotFoundException: Если диалог не найден.
        :raise LLMQueryException: В случае ошибки запроса к LLM.
        """
        title = "Ошибка запроса к LLM"
        headers = {"Content-Type": "application/json"}
        if idempotency_key:
            headers["X-Idempotency-Key"] = idempotency_key
        try:
            async with self._get_client(access_token) as client:
                resp = await client.post(
                    "/chat/llm/query",
                    headers=headers,
                    data=LLMQueryRequest(
                        conversation_id=conversation_id,
                        content=content,
                        temperature=temperature
                    ).model_dump_json()
                )
                resp.raise_for_status()
                return LLMQueryResponse(**resp.json())
        except HTTPStatusError as err:
            match err.response.status_code:
                case status.HTTP_403_FORBIDDEN:
                    logger.error(
                        f"Доступ к диалогу \"{conversation_id}\" запрещен"
                    )
                    raise errors.AccessException(
                        "Доступ запрещен",
                        _id=conversation_id
                    )
                case status.HTTP_404_NOT_FOUND:
                    logger.error(f"Диалог \"{conversation_id}\" не найден")
                    raise errors.ConversationNotFoundException(
                        "Диалог не найден",
                        conversation_id=conversation_id
                    )
                case _:
                    logger.error(
                        f"{title}: {err.response.text} "
                        f"(status_code={err.response.status_code}"
                    )
                    raise errors.LLMQueryException(
                        err.response.text,
                        conversation_id=conversation_id,
                        content=content
                    )
        except TimeoutException:
            logger.error(f"{title}: timeout error")
            raise errors.LLMQueryException(
                "timeout error",
                conversation_id=conversation_id,
                content=content
            )
        except Exception as err:
            logger.error(
                f"{title}: {err} ({err.__class__.__name__})"
            )
            raise errors.LLMQueryException(
                title,
                conversation_id=conversation_id,
                content=content
            )

    @conv_error_handler(
        errors.GetConversationException,
        "Ошибка получения данных диалога"
    )
    async def get_conversation_info(
            self,
            access_token: str,
            conversation_id: UUID
    ) -> conv_schemas.ConversationResponse:
        """
        Получение данных диалога.

        :param access_token: Access token.
        :param conversation_id: Идентификатор диалога.
        :return: Данные диалога.

        :raise ConversationAccessException: Если доступ к диалогу запрещен.
        :raise ConversationNotFoundException: Если диалог не найден.
        :raise GetConversationException: В случае ошибки получения данных.
        """
        async with self._get_client(access_token) as client:
            resp = await client.get(
                "/conversation/info",
                params={"conversation_id": str(conversation_id)}
            )
            resp.raise_for_status()
            return conv_schemas.ConversationResponse(**resp.json())

    @msg_error_handler(
        errors.GetMessageException,
        "Ошибка получения данных сообщения"
    )
    async def get_message(
            self,
            access_token: str,
            message_id: UUID
    ) -> MessageResponse:
        """
        Получение сообщения.

        :param access_token: Access token.
        :param message_id: Идентификатор сообщения.
        :return: Ответ от сервиса chat_api.
        """
        async with self._get_client(access_token) as client:
            resp = await client.get(
                f"/conversation/messages/{message_id}"
            )
            resp.raise_for_status()
            return conv_schemas.MessageResponse(**resp.json())

    async def admin_task_status(
            self,
            access_token: str,
            task_id: UUID
    ) -> CeleryTaskResponse:
        """
        Получение статуса задачи.

        :param access_token: Access token.
        :param task_id: Идентификатор задачи.
        :return: Данные о статусе задачи.

        :raise AccessException: Если доступ запрещен.
        :raise GetTaskStatusException: В случае ошибки получения статуса.
        """
        try:
            async with self._get_client(access_token) as client:
                resp = await client.get(f"/admin/tasks/{task_id}/status")
                resp.raise_for_status()
        except HTTPStatusError as err:
            match err.response.status_code:
                case status.HTTP_403_FORBIDDEN:
                    logger.error(
                        f"Доступ к эндпоинту разрешен только администраторам"
                    )
                    raise errors.AccessException(
                        "Доступ запрещен",
                        _id=task_id
                    )
                case status.HTTP_404_NOT_FOUND:
                    logger.error(f"Задача \"{task_id}\" не найдена")
                    raise errors.TaskNotFoundException(
                        "Задача не найдена",
                        task_id=task_id
                    )
                case _:
                    logger.error(
                        f"Ошибка получения статуса задачи: "
                        f"{err.response.text} "
                        f"(status_code={err.response.status_code}"
                    )
                    raise errors.GetTaskStatusException(err.response.text)
        except Exception as err:
            logger.error(
                f"Ошибка получения статуса задачи: "
                f"{err} ({err.__class__.__name__})"
            )
            raise errors.GetTaskStatusException(
                "Не удалось получить статус задачи"
            )
        return CeleryTaskResponse(**resp.json())
