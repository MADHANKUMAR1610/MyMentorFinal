import asyncio

from sqlalchemy import text
from app.database.database import engine


async def main():
    async with engine.begin() as conn:

        print("Current Alembic version:")

        result = await conn.execute(
            text("SELECT version_num FROM alembic_version")
        )

        rows = result.fetchall()

        for row in rows:
            print("  ", row[0])

        print("\nRemoving broken Alembic version...")

        await conn.execute(
            text("DELETE FROM alembic_version")
        )

        print("Alembic version reset successfully.")


if __name__ == "__main__":
    asyncio.run(main())