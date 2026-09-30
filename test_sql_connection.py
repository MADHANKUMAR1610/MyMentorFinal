import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

DATABASE_URL = os.getenv("SQL_SANDBOX_DATABASE_URL")


async def main():

    if not DATABASE_URL:
        print(
            "ERROR: SQL_SANDBOX_DATABASE_URL "
            "environment variable is not set."
        )
        return

    print("SQL sandbox URL found.")

    engine = create_async_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=1,
        max_overflow=0,
    )

    try:

        async with engine.connect() as connection:

            print("Database connection successful!")

            result = await connection.execute(
                text("SELECT current_database();")
            )

            print(
                "DATABASE:",
                result.scalar()
            )

            result = await connection.execute(
                text("SELECT * FROM students;")
            )

            rows = result.fetchall()

            print("\nSTUDENTS:")

            for row in rows:
                print(row)

    except Exception as exc:

        print("\nDATABASE ERROR:")
        print(repr(exc))

    finally:

        await engine.dispose()


asyncio.run(main())