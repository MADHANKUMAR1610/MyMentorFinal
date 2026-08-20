import asyncio
import asyncpg

DATABASE_URL = "postgresql://my_mentor_user:ffP9qVt7jV10em55Q6demBMRTe7WXMp1@dpg-da22tis9v7es738ipmrg-a.virginia-postgres.render.com/my_mentor"


async def fix():
    print("Connecting to database...")

    conn = await asyncpg.connect(DATABASE_URL)

    print("Connected successfully.")

    # Set Alembic to the latest migration that still exists
    await conn.execute("""
        UPDATE alembic_version
        SET version_num = '48f253fba588';
    """)

    print("Alembic version updated to 48f253fba588")

    await conn.close()


asyncio.run(fix())