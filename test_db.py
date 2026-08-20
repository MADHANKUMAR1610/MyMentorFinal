import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# asyncpg does not support the SQLAlchemy "+asyncpg" scheme
DATABASE_URL = DATABASE_URL.replace(
    "postgresql+asyncpg://",
    "postgresql://",
)

async def test():
    print("Testing database connection...")

    conn = await asyncpg.connect(DATABASE_URL)

    result = await conn.fetchval(
        "SELECT version();"
    )

    print("\nCONNECTED SUCCESSFULLY")
    print(result)

    await conn.close()


asyncio.run(test())