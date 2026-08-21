import asyncio

from sqlalchemy import text
from app.database.database import engine


async def main():
    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT version_num FROM alembic_version")
        )

        rows = result.fetchall()

        print("Alembic version:")
        for row in rows:
            print(row[0])


if __name__ == "__main__":
    asyncio.run(main())