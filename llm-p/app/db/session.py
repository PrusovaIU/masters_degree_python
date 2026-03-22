from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{settings.sqlite_path}"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)
