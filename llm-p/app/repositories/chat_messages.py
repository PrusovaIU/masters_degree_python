from loguru import logger
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import chat_messages as chat_messages_errors
from app.db.models import ChatMessage


class ChatMessageRepository:
    """
    Репозиторий для работы с таблицей chat_message.

    :param session: асинхронная сессия SQLAlchemy.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(
            self,
            user_id: int,
            role: str,
            content: str
    ) -> ChatMessage:
        """
        Создать новое сообщение.

        :param user_id: ID пользователя
        :param role: Роль отправителя.
        :param content: Текст сообщения.

        :return: Созданное сообщение

        :raises app.core.chat_messages.CreateMessageException:
            если не удалось создать сообщение.
        """
        message = ChatMessage(
            user_id=user_id,
            role=role,
            content=content
        )
        try:
            self._session.add(message)
            await self._session.commit()
            await self._session.refresh(message)
        except IntegrityError as err:
            err_txt = f"unknown user_id={user_id}"
            logger.error(f"Cannot create chat message: {err_txt} ({err})")
            raise chat_messages_errors.CreateMessageException(err_txt)
        except SQLAlchemyError as err:
            logger.error(
                f"Cannot create chat message: {err} "
                f"({err.__class__.__name__})"
            )
            raise chat_messages_errors.CreateMessageException(err) from err
        return message

    async def get_user_messages(
            self,
            user_id: int,
            limit: int = 10
    ) -> list[ChatMessage]:
        """
        Получить последние N сообщений пользователя.

        :param user_id: ID пользователя
        :param limit: Количество сообщений (по умолчанию 10)

        :return: Список сообщений, отсортированных по времени создания
            (от старых к новым).
        """
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_history_amount(self, user_id: int) -> int:
        """
        Получить количество сообщений пользователя.

        :param user_id: ID пользователя.
        :return: Количество сообщений.
        """
        stmt = (
            select(func.count())
            .select_from(ChatMessage)
            .where(ChatMessage.user_id == user_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar()

    async def delete_user_history(self, user_id: int) -> int:
        """
        Удалить всю историю сообщений пользователя.

        :param user_id: ID пользователя.
        :return: Количество удаленных сообщений.
        """
        stmt = (delete(ChatMessage).
                where(ChatMessage.user_id == user_id).
                returning(ChatMessage.id))
        result = await self._session.execute(stmt)
        await self._session.commit()
        return len(result.scalars().all())
