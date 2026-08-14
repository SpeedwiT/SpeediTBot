"""دیتابیس - اتصال و مدیریت سشن"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from config import settings


class Base(DeclarativeBase):
    pass


# Database URL
DATABASE_URL = (
    f"postgresql+asyncpg://{settings.database.user}:{settings.database.password}"
    f"@{settings.database.host}:{settings.database.port}/{settings.database.name}"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.app.debug,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db():
    """ایجاد جداول دیتابیس"""
    from database.models import Base as ModelsBase
    async with engine.begin() as conn:
        await conn.run_sync(ModelsBase.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """دریافت سشن دیتابیس - سازگار با FastAPI Depends"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db():
    """بستن اتصال دیتابیس"""
    await engine.dispose()
