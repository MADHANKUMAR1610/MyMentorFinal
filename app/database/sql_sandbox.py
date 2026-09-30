from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


from app.core.config import settings


sql_sandbox_engine = create_async_engine(
    settings.SQL_SANDBOX_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)


SQLSandboxSessionLocal = async_sessionmaker(
    bind=sql_sandbox_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_sql_sandbox_session() -> AsyncGenerator[
    AsyncSession,
    None,
]:

    async with SQLSandboxSessionLocal() as session:

        try:
            yield session

        finally:
            await session.close()