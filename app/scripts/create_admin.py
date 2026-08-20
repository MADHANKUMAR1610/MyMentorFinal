import asyncio

from sqlalchemy import select

from app.core.security import hash_password
from app.database.database import AsyncSessionLocal
from app.models.user import User


ADMIN_EMAIL = "admin@mymentor.com"
ADMIN_PASSWORD = "Admin@123"
ADMIN_NAME = "SkillHub Admin"


async def create_admin():
    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.email == ADMIN_EMAIL
            )
        )

        existing_user = result.scalar_one_or_none()

        # --------------------------------------------------
        # Admin already exists
        # --------------------------------------------------
        if existing_user:
            print("Admin user already exists.")

            existing_user.role = "admin"
            existing_user.is_active = True
            existing_user.is_verified = True

            await session.commit()

            print(f"Admin verified: {ADMIN_EMAIL}")
            return

        # --------------------------------------------------
        # Create new admin
        # --------------------------------------------------
        admin = User(
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            name=ADMIN_NAME,
            role="admin",
            is_active=True,
            is_verified=True,
            onboarded=True,
        )

        session.add(admin)

        await session.commit()
        await session.refresh(admin)

        print("====================================")
        print("Admin created successfully")
        print(f"Email: {ADMIN_EMAIL}")
        print(f"Password: {ADMIN_PASSWORD}")
        print(f"Role: {admin.role}")
        print("====================================")


if __name__ == "__main__":
    asyncio.run(create_admin())