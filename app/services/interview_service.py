from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.organization_repository import (
    OrganizationRepository,
)
from app.repositories.interview_repository import (
    InterviewRepository,
)


class InterviewService:

    def __init__(self, db: AsyncSession):

        self.organization_repository = (
            OrganizationRepository(db)
        )

        self.interview_repository = (
            InterviewRepository(db)
        )

    # ============================================================
    # CREATE INTERVIEW
    # ============================================================

    async def create_interview(
        self,
        user_id: UUID,
        *,
        application_id: UUID,
        interviewer_id: UUID,
        title: str,
        interview_type: str,
        scheduled_at,
        duration_minutes: int,
        mode: str,
        meeting_link: str | None,
        location: str | None,
        notes: str | None,
    ):

        # --------------------------------------------------------
        # 1. GET ORGANIZATION OF LOGGED-IN USER
        # --------------------------------------------------------

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        # --------------------------------------------------------
        # 2. CHECK APPLICATION EXISTS
        # --------------------------------------------------------

        application = await (
            self.interview_repository
            .get_application_by_id(
                application_id=application_id,
                company_id=company.id,
            )
        )

        if application is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found.",
            )

        # --------------------------------------------------------
        # 3. CHECK INTERVIEWER EXISTS
        # --------------------------------------------------------

        interviewer = await (
            self.interview_repository
            .get_user_by_id(
                interviewer_id
            )
        )

        if interviewer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interviewer not found.",
            )

        # --------------------------------------------------------
        # 4. CHECK INTERVIEWER BELONGS TO ORGANIZATION
        # --------------------------------------------------------

        if interviewer.company_id != company.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interviewer does not belong to this organization.",
            )

        # --------------------------------------------------------
        # 5. CREATE INTERVIEW
        # --------------------------------------------------------

        interview = await (
            self.interview_repository.create(
                company_id=company.id,
                application_id=application_id,
                interviewer_id=interviewer_id,
                title=title,
                interview_type=interview_type,
                scheduled_at=scheduled_at,
                duration_minutes=duration_minutes,
                mode=mode,
                meeting_link=meeting_link,
                location=location,
                notes=notes,
            )
        )

        return interview

    # ============================================================
    # GET ALL ORGANIZATION INTERVIEWS
    # ============================================================

    async def get_interviews(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ):

        # --------------------------------------------------------
        # GET ORGANIZATION OF LOGGED-IN USER
        # --------------------------------------------------------

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        # --------------------------------------------------------
        # GET ALL INTERVIEWS
        # --------------------------------------------------------

        interviews = await (
            self.interview_repository
            .get_by_company_id(
                company_id=company.id,
                skip=skip,
                limit=limit,
            )
        )

        return interviews
    
    # ============================================================
    # GET SINGLE ORGANIZATION INTERVIEW
    # ============================================================

    async def get_interview(
        self,
        user_id: UUID,
        interview_id: UUID,
    ):

        # --------------------------------------------------------
        # GET ORGANIZATION OF LOGGED-IN USER
        # --------------------------------------------------------

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        # --------------------------------------------------------
        # GET INTERVIEW
        # --------------------------------------------------------

        interview = await (
            self.interview_repository
            .get_by_id(
                interview_id=interview_id,
                company_id=company.id,
            )
        )

        if interview is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found.",
            )

        return interview
    # ============================================================
    # UPDATE ORGANIZATION INTERVIEW
    # ============================================================

    async def update_interview(
        self,
        user_id: UUID,
        interview_id: UUID,
        data: dict,
    ):

        # --------------------------------------------------------
        # 1. GET ORGANIZATION
        # --------------------------------------------------------

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        # --------------------------------------------------------
        # 2. GET INTERVIEW
        # --------------------------------------------------------

        interview = await (
            self.interview_repository
            .get_by_id(
                interview_id=interview_id,
                company_id=company.id,
            )
        )

        if interview is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found.",
            )

        # --------------------------------------------------------
        # 3. UPDATE ALLOWED FIELDS
        # --------------------------------------------------------

        allowed_fields = {
            "title",
            "interview_type",
            "scheduled_at",
            "duration_minutes",
            "mode",
            "meeting_link",
            "location",
            "notes",
        }

        for field, value in data.items():

            if field in allowed_fields and value is not None:
                setattr(interview, field, value)

        # --------------------------------------------------------
        # 4. SAVE
        # --------------------------------------------------------

        return await self.interview_repository.update(
            interview
        )
    # ============================================================
    # UPDATE INTERVIEW STATUS
    # ============================================================

    async def update_interview_status(
        self,
        user_id: UUID,
        interview_id: UUID,
        status: str,
    ):

        # --------------------------------------------------------
        # 1. GET ORGANIZATION
        # --------------------------------------------------------

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        # --------------------------------------------------------
        # 2. GET INTERVIEW
        # --------------------------------------------------------

        interview = await (
            self.interview_repository
            .get_by_id(
                interview_id=interview_id,
                company_id=company.id,
            )
        )

        if interview is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found.",
            )

        # --------------------------------------------------------
        # 3. VALIDATE STATUS
        # --------------------------------------------------------

        allowed_statuses = {
            "scheduled",
            "completed",
            "cancelled",
            "rescheduled",
            "no_show",
        }

        if status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid interview status. "
                    "Allowed values: scheduled, completed, "
                    "cancelled, rescheduled, no_show."
                ),
            )

        # --------------------------------------------------------
        # 4. UPDATE STATUS
        # --------------------------------------------------------

        interview.status = status

        # --------------------------------------------------------
        # 5. SAVE
        # --------------------------------------------------------

        return await (
            self.interview_repository.update(
                interview
            )
        )
    # ============================================================
    # UPDATE INTERVIEW FEEDBACK
    # ============================================================

    async def update_feedback(
        self,
        user_id: UUID,
        interview_id: UUID,
        *,
        rating: int | None = None,
        feedback: str | None = None,
        recommendation: str | None = None,
        notes: str | None = None,
    ):
        # --------------------------------------------------------
        # Find organization of logged-in user
        # --------------------------------------------------------

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        # --------------------------------------------------------
        # Get interview
        # --------------------------------------------------------

        interview = await (
            self.interview_repository
            .get_by_id(
                interview_id=interview_id,
                company_id=company.id,
            )
        )

        if interview is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found.",
            )

        # --------------------------------------------------------
        # Update only supplied fields
        # --------------------------------------------------------

        if rating is not None:
            interview.rating = rating

        if feedback is not None:
            interview.feedback = feedback

        if recommendation is not None:
            interview.recommendation = recommendation

        if notes is not None:
            interview.notes = notes

        # --------------------------------------------------------
        # Save changes
        # --------------------------------------------------------

        return await self.interview_repository.update(
            interview
        )

    # ============================================================
    # DELETE INTERVIEW
    # ============================================================

    async def delete_interview(
        self,
        user_id: UUID,
        interview_id: UUID,
    ):
        # --------------------------------------------------------
        # Find organization of logged-in user
        # --------------------------------------------------------

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        # --------------------------------------------------------
        # Get interview belonging to this organization
        # --------------------------------------------------------

        interview = await (
            self.interview_repository
            .get_by_id(
                interview_id=interview_id,
                company_id=company.id,
            )
        )

        if interview is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found.",
            )

        # --------------------------------------------------------
        # Delete interview
        # --------------------------------------------------------

        await self.interview_repository.delete(
            interview
        )

        return None