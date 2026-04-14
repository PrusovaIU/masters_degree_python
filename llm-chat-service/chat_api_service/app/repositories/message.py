from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, desc, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from chat_api_service.app.consts.message import MessageStatus
from chat_api_service.app.db.models import Message
from chat_api_service.app.schemas.message import MessageCreate


class MessageRepository:
    """
    Репозиторий для операций с сообщениями.
    """
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(
            self,
            conversation_id: UUID,
            message_in: MessageCreate,
            idempotency_key: str | None = None,
            llm_task_id: str | None = None,
    ) -> Message:
        """
        Создание нового сообщения.

        :param conversation_id: UUID диалога.
        :param message_in: Данные сообщения.
        :param idempotency_key: Ключ идемпотентности.
        :param llm_task_id: ID задачи Celery для LLM.
        :return: Созданный объект Message.
        """
        message = Message(
            conversation_id=conversation_id,
            sender_type=message_in.sender_type,
            content=message_in.content,
            status=message_in.status or MessageStatus.SENT,
            idempotency_key=idempotency_key,
            llm_task_id=llm_task_id,
            metadata_json=message_in.metadata,
        )
        self._session.add(message)
        await self._session.flush()
        return message

    async def get_by_id(
            self,
            message_id: UUID,
            conversation_id: UUID | None = None,
    ) -> Message | None:
        """
        Получение сообщения по ID.

        :param message_id: UUID сообщения.
        :param conversation_id: Опциональная проверка принадлежности диалогу.
        :return: Объект Message или None.
        """
        query = select(Message).where(Message.id == message_id)

        if conversation_id:
            query = query.where(Message.conversation_id == conversation_id)

        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(
            self,
            idempotency_key: str,
    ) -> Message | None:
        """
        Поиск сообщения по ключу идемпотентности.

        :param idempotency_key: Уникальный ключ запроса.
        :return: Найденное сообщение или None.
        """
        query = select(Message).where(
            Message.idempotency_key == idempotency_key
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_conversation(
            self,
            conversation_id: UUID,
            limit: int = 50,
            offset: int = 0
    ) -> Sequence[Message]:
        """
        Получение истории сообщений диалога с пагинацией.

        :param conversation_id: UUID диалога.
        :param limit: Максимальное количество сообщений.
        :param offset: Смещение для пагинации.
        :return: Список сообщений в хронологическом порядке.
        """
        query = select(Message).where(
            Message.conversation_id == conversation_id
        )

        # Сортировка и пагинация
        query = (
            query.order_by(
                desc(Message.created_at)
            ).limit(limit)
            .offset(offset)
        )

        result = await self._session.execute(query)
        messages = result.scalars().all()

        return messages

    async def count_by_conversation(
            self,
            conversation_id: UUID
    ) -> int:
        """
        Подсчёт количества сообщений в диалоге.

        :param conversation_id: UUID диалога.
        :return: Количество сообщений.
        """
        query = select(func.count()).where(
            Message.conversation_id == conversation_id)

        result = await self._session.execute(query)
        return result.scalar_one()

    async def update_status(
            self,
            message_id: UUID,
            new_status: MessageStatus | str,
            conversation_id: UUID | None = None,
    ) -> Message | None:
        """
        Обновление статуса сообщения с валидацией перехода.

        :param message_id: UUID сообщения.
        :param new_status: Новый статус.
        :param conversation_id: Опциональная проверка принадлежности.
        :return: Обновлённое сообщение или None.
        :raises ValueError: Если переход статуса недопустим.
        """
        message = await self.get_by_id(message_id, conversation_id)
        if not message:
            return None

        message.update_status(new_status)
        await self._session.flush()
        return message

    async def update_llm_task_id(
            self,
            message_id: UUID,
            llm_task_id: str,
    ) -> bool:
        """
        Привязка ID задачи Celery к сообщению.

        :param message_id: UUID сообщения.
        :param llm_task_id: ID задачи Celery.
        :return: True если успешно обновлено.
        """
        result = await self._session.execute(
            update(Message)
            .where(
                Message.id == message_id,
                Message.llm_task_id.is_(None),
            )
            .values(
                llm_task_id=llm_task_id,
                status=MessageStatus.PROCESSING
            )
            .execution_options(synchronize_session="fetch")
        )
        return result.rowcount > 0

    async def update_content_and_metadata(
            self,
            message_id: UUID,
            content: str | None = None,
            metadata: dict | None = None,
    ) -> Message | None:
        """
        Обновление контента и метаданных сообщения (для ответов LLM).

        :param message_id: UUID сообщения.
        :param content: Новый текст сообщения.
        :param metadata: Дополнительные метаданные.
        :return: Обновлённое сообщение или None.
        """
        message = await self.get_by_id(message_id)
        if not message:
            return None

        if content is not None:
            message.content = content
        if metadata is not None:
            current_meta = message.metadata_json or {}
            message.metadata_json = {**current_meta, **metadata}

        message.updated_at = datetime.now(timezone.utc)
        await self._session.flush()
        return message
