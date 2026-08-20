import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def reset_alembic():
    print("Connecting to database...")

    database_url = DATABASE_URL.replace(
        "postgresql+asyncpg://",
        "postgresql://"
    )

    conn = await asyncpg.connect(database_url)

    print("Connected successfully.")

    await conn.execute("DELETE FROM alembic_version")

    print("Alembic version reset successfully.")

    await conn.close()

asyncio.run(reset_alembic())