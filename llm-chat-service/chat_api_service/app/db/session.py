from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from loguru import logger
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)


class DBSession:
    """Класс для работы с сессией БД"""
    _engine : AsyncEngine | None = None
    _async_session_maker: async_sessionmaker[AsyncSession] | None = None
    _has_setup: bool = False

    @classmethod
    def engine(cls) -> AsyncEngine | None:
        return cls._engine

    @classmethod
    def is_initialized(cls) -> bool:
        """
        :return: True, если класс был инициализирован, иначе False.
        """
        return cls._has_setup

    @staticmethod
    def _form_connect_args(
            data_base_url: str,
            schema: str = "public"
    ) -> dict:
        if "postgresql" in data_base_url:
            return {"server_settings": {"search_path": f"{schema}"}}
        else:
            return {}

    @classmethod
    def setup(
            cls,
            data_base_url: str,
            schema: str = "public",
            has_setup: bool = False
    ) -> None:
        """
        Инициализация класса.

        :param data_base_url: Строка подключения к БД.

        :param schema: Схема БД.

        :param has_setup: Если False и класс уже был инициализирован, то
            выбрасывается исключение.

        :return: None
        """
        if cls._has_setup:
            if not has_setup:
                msg = f"Класс {cls.__name__} уже был инициализирован."
                logger.warning(msg)
                raise SystemError(msg)
            else:
                return
        connect_args = cls._form_connect_args(data_base_url, schema)
        cls._engine = create_async_engine(
            data_base_url,
            connect_args=connect_args
        )
        cls._async_session_maker = async_sessionmaker(
            cls._engine,
            expire_on_commit=False
        )
        cls._has_setup = True
        logger.info(f"Инициализация класса {cls.__name__} завершена.")

    @classmethod
    async def close(cls) -> None:
        """
        Очистка класса.
        :return: None.
        """
        if cls._has_setup:
            await cls._engine.dispose()
            cls._has_setup = False
            cls._engine = None
            cls._async_session_maker = None
            logger.info(f"Закрытие класса {cls.__name__}.")

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
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
