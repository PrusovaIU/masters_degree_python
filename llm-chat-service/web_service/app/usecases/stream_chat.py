import asyncio
import json
from collections.abc import AsyncGenerator, Callable
from uuid import UUID

from web_service.app.services.chat_client import ChatAPIServiceClient
from libs.schemas import conversation as schemas
from math import ceil
from libs.schemas.llm_query import LLMQueryResponse
from web_service.app.core.exceptions import chat_api_client as errors
from contextlib import asynccontextmanager

from web_service.app.infra.rabbitmq import RabbitMQClient
from loguru import logger
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import partial


class StreamChatUsecase:
    def __init__(
            self,
            rabbit_client: RabbitMQClient,
            chat_api_client: ChatAPIServiceClient,
            queue_prefix: str
    ):
        self._rabbit_client = rabbit_client
        self._chat_api_client = chat_api_client
        self._queue_prefix = queue_prefix

    async def event_generator(
            self,
            access_token: str,
            conversation_id: UUID
    ) -> Callable[[], AsyncGenerator[str]]:
        """
        Создание итератора для получения сообщений из диалога.

        :param access_token: Access token.
        :param conversation_id: Идентификатор диалога.
        :return: Итератор для потребления сообщений.

        :raise ConversationAccessException: Если доступ к диалогу запрещен.
        :raise ConversationNotFoundException: Если диалог не найден.
        :raise GetConversationException: В случае ошибки получения данных.
        """
        # Проверка доступа к диалогу:
        await self._chat_api_client.get_conversation_info(
            access_token, conversation_id
        )
        queue_name = f"{self._queue_prefix}_{conversation_id}"

        return partial(
            self._rabbit_client.consume_messages,
            queue_name=queue_name
        )

