from collections.abc import AsyncGenerator
from uuid import UUID

from web_service.app.infra.rabbitmq import RabbitMQClient
from web_service.app.services.chat_client import ChatAPIServiceClient


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
    ) -> AsyncGenerator[str, None]:
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
            access_token=access_token,
            conversation_id=conversation_id
        )
        queue_name = f"{self._queue_prefix}_{conversation_id}"

        async for message in self._rabbit_client.consume_messages(
                queue_name=queue_name):
            yield message
