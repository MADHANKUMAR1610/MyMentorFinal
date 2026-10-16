
import asyncio
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine


async def main():
    engine = create_async_engine(settings.DATABASE_URL)

    try:
        async with engine.connect() as connection:
            print("DATABASE CONNECTION SUCCESS")

    except Exception as exc:
        print("DATABASE CONNECTION FAILED")
        print(type(exc).__name__)
        print(str(exc))

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
