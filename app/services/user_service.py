from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.repository = UserRepository(session)

    # =========================================================
    # GET USER BY ID
    # =========================================================

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:

        return await self.repository.get_by_id(
            user_id
        )

    # =========================================================
    # GET USER BY EMAIL
    # =========================================================

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:

        return await self.repository.get_by_email(
            email
        )

    # =========================================================
    # GET USER BY PHONE
    # =========================================================

    async def get_by_phone(
        self,
        phone: str,
    ) -> User | None:

        return await self.repository.get_by_phone(
            phone
        )

    # =========================================================
    # CREATE USER
    # =========================================================

    async def create_user(
        self,
        user: User,
    ) -> User:

        return await self.repository.create(
            user
        )

    # =========================================================
    # UPDATE USER
    # =========================================================

    async def update_user(
        self,
        user: User,
    ) -> User:

        return await self.repository.update(
            user
        )

    # =========================================================
    # DELETE USER
    # =========================================================

    async def delete_user(
        self,
        user: User,
    ) -> None:

        await self.repository.delete(
            user
        )

    # =========================================================
    # GET ALL STUDENTS WITH PROGRESS
    # =========================================================

    async def get_students_with_progress(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ):

        return await self.repository.get_students_with_progress(
            skip=skip,
            limit=limit,
        )

    # =========================================================
    # GET STUDENT STREAK
    # =========================================================

    async def get_student_streak(
        self,
        user_id: UUID,
    ) -> int:

        return await self.repository.get_student_streak(
            user_id
        )