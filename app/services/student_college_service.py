from fastapi import HTTPException, status
from sqlalchemy import select

from app.models.college import College
from app.models.user import User


class StudentCollegeService:

    def __init__(self, session):
        self.session = session

    async def link_college_by_student_code(
        self,
        current_user: User,
        student_code: str,
    ) -> College:

        code = student_code.strip().upper()

        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student ID is required.",
            )

        # --------------------------------------------------
        # FIND STUDENT BY STUDENT CODE
        # --------------------------------------------------

        result = await self.session.execute(
            select(User).where(
                User.student_code == code
            )
        )

        student = result.scalar_one_or_none()

        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid student ID.",
            )

        # --------------------------------------------------
        # MAKE SURE THE CODE BELONGS TO LOGGED-IN USER
        # --------------------------------------------------

        if student.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This student ID does not belong to the logged-in user.",
            )

        # --------------------------------------------------
        # STUDENT MUST HAVE A COLLEGE
        # --------------------------------------------------

        if student.college_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No college is assigned to this student.",
            )

        # --------------------------------------------------
        # FIND COLLEGE
        # --------------------------------------------------

        college_result = await self.session.execute(
            select(College).where(
                College.id == student.college_id
            )
        )

        college = college_result.scalar_one_or_none()

        if college is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="College not found.",
            )

        # --------------------------------------------------
        # CHECK COLLEGE STATUS
        # --------------------------------------------------

        if college.status.lower() != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This college is currently inactive.",
            )

        # --------------------------------------------------
        # SAVE COLLEGE TO LOGGED-IN USER
        # --------------------------------------------------

        current_user.college_id = college.id

        await self.session.commit()
        await self.session.refresh(current_user)

        return college