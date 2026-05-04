from uuid import UUID

from web_service.app.services.chat_client import ChatAPIServiceClient
from libs.schemas import conversation as schemas
from math import ceil
from libs.schemas.llm_query import LLMQueryResponse


class ChatUsecase:
    def __init__(self, chat_api_client: ChatAPIServiceClient):
        self._chat_api_client = chat_api_client

    async def conversation_all(
            self,
            access_token: str,
            limit: int,
            page: int
    ) -> tuple[dict[UUID, str], int, int]:
        """
        Запрос списка всех диалогов.

        :param access_token: Access token пользователя.
        :param limit: Количество диалогов на странице.
        :param page: Страница.

        :return: Список диалогов {UUID диалога: название диалога},
            количество страниц,
            общее количество диалогов.
        """
        offset = (page - 1) * limit
        response: schemas.ConversationListResponse = \
            await self._chat_api_client.list_conversations(
                access_token, limit, offset
            )
        conversations = {c.id: c.title for c in response.conversations}
        total_page = ceil(response.pagination.total / limit)
        return conversations, total_page, response.pagination.total

    async def new_conversation(
            self,
            access_token: str,
            title: str
    ) -> schemas.ConversationCreateResponse:
        """
        Создание нового диалога.

        :param access_token: Access token пользователя.
        :param title: Заголовок диалога.
        :return: Данные нового диалога.
        """
        return await self._chat_api_client.create_conversation(
            access_token, title
        )

    async def conversation_history(
            self,
            access_token: str,
            conversation_id: UUID,
            limit: int,
            page: int
    ) -> tuple[dict[UUID, str], int, int]:
        """
        Получение истории диалога.

        :param access_token: Access token пользователя.
        :param conversation_id: ID диалога.
        :param limit: Количество сообщений на странице.
        :param page: Номер страницы.

        :return: Список сообщений {UUID сообщения: текст сообщения},
            количество страниц,
            общее количество сообщений.
        """
        offset = (page - 1) * limit
        response: schemas.ConversationHistoryResponse = \
            await self._chat_api_client.get_conversation_history(
                access_token, conversation_id, limit, offset
            )
        messages = {m.id: m.text for m in response.messages}
        total_page = ceil(response.pagination.total / limit)
        return messages, total_page, response.pagination.total

    async def send_message(
            self,
            access_token: str,
            conversation_id: UUID,
            content: str,
            temperature: float
    ) -> UUID:
        """
        Отправка сообщения в диалог.

        :param access_token: Access token пользователя.
        :param conversation_id: Идентификатор диалога.
        :param content: Содержимое сообщения.
        :param temperature: Температура генерации ответа.
        :return: Идентификатор сообщения.
        """
        response: LLMQueryResponse = await self._chat_api_client.query_llm(
            access_token, conversation_id, content, temperature
        )
        return response.message_id

