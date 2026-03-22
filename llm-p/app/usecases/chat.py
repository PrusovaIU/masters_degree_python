from app.db.models import ChatMessage
from app.repositories.chat_messages import ChatMessageRepository
from app.schemas.openrouter_message import Message
from app.services.openrouter_client import OpenRouterClient
from dataclasses import asdict
from app.consts.roles import Roles
from app.schemas.pagination import Pagination
from app.schemas.chat import ChatHistoryResponse, ChatMessageResponse


class ChatUseCase:
    """
    UseCase для общения с LLM через чат.

    :param message_repository: Репозиторий сообщений чата.
    :param openrouter_client: Клиент OpenRouter.
    """

    def __init__(
            self,
            message_repository: ChatMessageRepository,
            openrouter_client: OpenRouterClient
    ):
        self._message_repo = message_repository
        self._openrouter_client = openrouter_client

    async def _form_message(
            self,
            user_id: int,
            user_role: str,
            prompt: str,
            system: str | None = None,
            max_history: int = 10
    ) -> list[dict[str, str]]:
        """
        Формирование сообщений для запроса к LLM.

        :param user_id: ID пользователя
        :param user_role: Роль пользователя
        :param prompt: Текст запроса
        :param system: Системная инструкция (опционально)
        :param max_history: Количество сообщений из истории для контекста.
        :return: Совокупность сообщений.
        """
        messages: list[Message] = []
        if system:
            messages.append(Message(role=Roles.system, content=system))
        history: list[ChatMessage] = \
            await self._message_repo.get_user_messages(
                user_id, max_history
            )
        for msg in history:
            messages.append(Message(role=msg.role, content=msg.content))
        messages.append(Message(role=user_role, content=prompt))
        return [asdict(msg) for msg in messages]

    async def ask(
            self,
            user_id: int,
            user_role: str,
            prompt: str,
            system: str | None = None,
            max_history: int = 10,
            temperature: float = 0.7
    ) -> str:
        """
        Отправить запрос к LLM и получить ответ.

        :param user_id: ID пользователя
        :param user_role: Роль пользователя
        :param prompt: Текст запроса
        :param system: Системная инструкция (опционально)
        :param max_history: Количество сообщений из истории для контекста
        :param temperature: Параметр креативности

        :return: Ответ модели.

        :raises app.core.errors.openrouter_client.OpenRouterClientException:
            Если запрос к API не удался.

        :raises app.core.chat_messages.ChatMessageRepositoryException:
            Если не удалось внести изменения в БД.
        """
        messages = await self._form_message(
            user_id, user_role, prompt, system, max_history
        )
        await self._message_repo.create(
            user_id=user_id,
            role=user_role,
            content=prompt
        )
        answer: str = await self._openrouter_client.chat_completion(
            messages=messages,
            temperature=temperature
        )
        await self._message_repo.create(
            user_id=user_id,
            role=Roles.assistant,
            content=answer
        )
        return answer

    async def history(
            self,
            user_id: int,
            max_history: int = 10
    ) -> ChatHistoryResponse:
        """
        Получение истории сообщений пользователя.

        :param user_id: ID пользователя.
        :param max_history: Максимальная длина истории.
        :return: Список сообщений.
        """
        msgs_amount: int = await self._message_repo.get_user_history_amount(
            user_id
        )
        data: list[ChatMessage] = await self._message_repo.get_user_messages(
            user_id, max_history
        )
        return ChatHistoryResponse(
            data=[ChatMessageResponse.model_validate(row) for row in data],
            pagination=Pagination(
                limit=max_history,
                total=msgs_amount
            )
        )

    async def clear_history(self, user_id: int) -> int:
        """
        Очистка истории сообщений пользователя.

        :param user_id: ID пользователя.
        :return: Количество удаленных сообщений.
        """
        return await self._message_repo.delete_user_history(user_id)
