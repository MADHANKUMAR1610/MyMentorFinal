import asyncio

from app.database.database import AsyncSessionLocal
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password


async def test():
    async with AsyncSessionLocal() as session:
        repository = UserRepository(session)

        user = await repository.get_by_email(
            "madhan@gmail.com"
        )

        print("USER FOUND:", user is not None)

        if user:
            print("EMAIL:", user.email)
            print("HASH EXISTS:", bool(user.password_hash))
            print("HASH:", user.password_hash)

            print(
                "PASSWORD MATCH:",
                verify_password(
                    "madhan@2003",
                    user.password_hash,
                )
            )


asyncio.run(test())
