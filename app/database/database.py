
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


# Normalize the database URL and explicitly set PostgreSQL's default port.
database_url = make_url(settings.DATABASE_URL)

if database_url.drivername == "postgresql":
    database_url = database_url.set(drivername="postgresql+asyncpg")

if database_url.port is None:
    database_url = database_url.set(port=5432)


engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=5,
    pool_timeout=30,
    connect_args={
        "timeout": 30,
        "command_timeout": 30,
    },
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
