from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, \
    AsyncEngine, AsyncSession

from loguru import logger
from warnings import warn
from contextlib import asynccontextmanager


class DBSession:
    """Класс для работы с сессией БД"""
    _engine : AsyncEngine | None = None
    _async_session_maker: async_sessionmaker | None = None
    _has_setup: bool = False

    @classmethod
    def setup(cls, data_base_url: str) -> None:
        """
        Инициализация класса.

        :param data_base_url: Строка подключения к БД.
        :return: None
        """
        if cls._has_setup:
            warn_msg = f"Класс {cls.__name__} уже был инициализирован."
            logger.warning(warn_msg)
            raise warn(warn_msg, RuntimeWarning)
        cls._engine = create_async_engine(data_base_url)
        cls._async_session_maker = async_sessionmaker(
            cls._engine,
            expire_on_commit=False
        )
        cls._has_setup = True
        logger.info(f"Инициализация класса {cls.__name__} завершена.")

    @classmethod
    @asynccontextmanager
    async def get_async_session(cls) -> AsyncGenerator[AsyncSession]:
        """
        Контекстный менеджер для работы с сессией БД.
        Создает новую сессию и закрывает ее после выполнения блока. Если в
        процессе выполнения блока возникнет ошибка, то сессия будет откатана,
        иначе commit.

        :yield: Сессия БД.
        :return: None.
        """
        if not cls._has_setup:
            raise SystemError(
                f"Класс {cls.__name__} не был инициализирован. "
                f"Используйте метод setup()"
            )
        session = cls._async_session_maker()
        try:
            yield session
            await session.commit()
        except Exception as err:
            await session.rollback()
            raise err
        finally:
            await session.close()
