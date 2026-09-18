from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.college_repository import (
    CollegeRepository,
)


class StudentCollegeService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

        self.college_repository = (
            CollegeRepository(session)
        )

    # ========================================================
    # LINK STUDENT TO COLLEGE
    # ========================================================

    async def link_college(
        self,
        user: User,
        college_code: str,
    ):

        # ----------------------------------------------------
        # STUDENT CHECK
        # ----------------------------------------------------

        if user.role != "student":

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Only students can link "
                    "a college."
                ),
            )

        # ----------------------------------------------------
        # CLEAN CODE
        # ----------------------------------------------------

        code = college_code.strip().upper()

        if not code:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="College code is required.",
            )

        # ----------------------------------------------------
        # FIND COLLEGE
        # ----------------------------------------------------

        college = (
            await self.college_repository.get_by_code(
                code
            )
        )

        if college is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Invalid college code. "
                    "College not found."
                ),
            )

        # ----------------------------------------------------
        # CHECK COLLEGE STATUS
        # ----------------------------------------------------

        if college.status != "active":

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "This college is currently "
                    "not active."
                ),
            )

        # ----------------------------------------------------
        # LINK COLLEGE
        # ----------------------------------------------------

        user.college_id = college.id

        await self.session.commit()

        await self.session.refresh(
            user
        )

        return college