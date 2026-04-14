from collections.abc import Sequence
from uuid import UUID

from loguru import logger
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from chat_api_service.app.core.exceptions.conversation import \
    ConversationAccessDenied, ConversationNotFound
from chat_api_service.app.db.models import Conversation, Message


class ConversationRepository:
    """
    Репозиторий для операций с диалогами.
    """
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(
            self,
            user_id: str,
            title: str
    ) -> Conversation:
        """
        Создание нового диалога.

        :param user_id: ID пользователя из Auth Service.
        :param title: Заголовок диалога.
        :return: Созданный объект Conversation.
        """
        conversation = Conversation(
            user_id=user_id,
            title=title,
        )
        self._session.add(conversation)
        await self._session.flush()
        return conversation

    async def get_by_id(
            self,
            conversation_id: UUID,
            user_id: str | None = None
    ) -> Conversation | None:
        """
        Получение диалога по ID.

        :param conversation_id: UUID диалога.
        :param user_id: Опциональная проверка принадлежности пользователю.
        :return: Объект Conversation или None.
        """
        query = select(Conversation).where(Conversation.id == conversation_id)

        if user_id:
            query = query.where(Conversation.user_id == user_id)

        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get(
            self,
            conversation_id: UUID,
            user_id: str | None = None
    ) -> Conversation:
        """
        Получение диалога.

        :param conversation_id: UUID диалога.

        :param user_id: Идентификатор пользователя для проверки доступа.
            Если None, доступ не проверяется.

        :return: Диалог.

        :raises ConversationNotFound: Если диалог не найден.

        :raises ConversationAccessDenied: Если доступ к диалогу запрещён.
        """
        conversation = await self.get_by_id(
            conversation_id=conversation_id,
            user_id=user_id
        )

        if not conversation and user_id:
            conv_without_auth = await self.get_by_id(
                conversation_id=conversation_id
            )
            if conv_without_auth:
                logger.warning(
                    f"Доступ к диалогу {conversation_id} запрещён "
                    f"для пользователя {user_id}"
                )
                raise ConversationAccessDenied(
                    f"Доступ к диалогу {conversation_id} запрещён",
                    conversation_id=conversation_id,
                    user_id=user_id
                )
        if not conversation:
            logger.warning(f"Диалог {conversation_id} не найден")
            raise ConversationNotFound(
                f"Диалог {conversation_id} не найден",
                conversation_id=conversation_id
            )
        return conversation

    async def list_by_user(
            self,
            user_id: str,
            limit: int | None = None,
            offset: int | None = None
    ) -> tuple[Sequence[Conversation], int]:
        """
        Получение списка диалогов пользователя с пагинацией.

        :param user_id: ID пользователя.
        :param limit: Количество элементов на странице.
        :param offset: Смещение для пагинации.
        :return: (список диалогов, общее количество).
        """
        query = select(Conversation).where(Conversation.user_id == user_id)

        # Получение общего количества для пагинации
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self._session.execute(count_query)
        total: int = count_result.scalar_one()

        # Применение пагинации и сортировки
        query = query.order_by(desc(Conversation.updated_at))

        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        result = await self._session.execute(query)
        conversations = result.scalars().all()

        return conversations, total

    async def update(
            self,
            conversation_id: UUID,
            user_id: str,
            **update_data,
    ) -> Conversation | None:
        """
        Обновление диалога.

        :param conversation_id: UUID диалога.
        :param user_id: ID пользователя для проверки прав.
        :param update_data: Поля для обновления.
        :return: Обновлённый объект или None.
        """
        # Проверка существования диалога
        conversation = await self.get_by_id(conversation_id, user_id)
        if not conversation:
            raise ValueError(
                f"Диалога с ID={conversation_id} не существует или "
                f"недоступен для пользователя."
            )

        for key, value in update_data.items():
            if hasattr(conversation, key) and value is not None:
                setattr(conversation, key, value)

        await self._session.flush()
        return conversation

    async def delete(
            self,
            conversation_id: UUID,
            user_id: str,
    ) -> bool:
        """
        Удаление диалога (каскадно удалит сообщения).

        :param conversation_id: UUID диалога.
        :param user_id: ID пользователя для проверки прав.
        :return: True если успешно, False если диалог не найден.
        """
        conversation = await self.get_by_id(conversation_id, user_id)
        if not conversation:
            return False

        await self._session.delete(conversation)
        return True

    async def get_last_message_preview(
            self,
            conversation_id: UUID,
    ) -> str | None:
        """
        Получение превью последнего сообщения для списка диалогов.

        :param conversation_id: UUID диалога.
        :return: Текст последнего сообщения или None.
        """
        result = await self._session.execute(
            select(Message.content)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(1)
        )
        row = result.first()
        return row[0] if row else None
