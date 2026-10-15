
from uuid import UUID

from fastapi import HTTPException, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.organization_repository import (
    OrganizationRepository,
)
from app.repositories.interview_repository import (
    InterviewRepository,
)


class InterviewService:

    def __init__(self, db: AsyncSession):
        self.organization_repository = OrganizationRepository(db)
        self.interview_repository = InterviewRepository(db)

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
        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        application = await (
            self.interview_repository.get_application_by_id(
                application_id=application_id,
                company_id=company.id,
            )
        )

        if application is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Job application not found.",
            )

        interviewer = await (
            self.interview_repository.get_user_by_id(
                interviewer_id
            )
        )

        if interviewer is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Interviewer not found.",
            )

        if not interviewer.is_active:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="This interviewer account is inactive.",
            )

        
        allowed_roles = {
            "interviewer",
            "hiring_manager",
        }

        if interviewer.role not in allowed_roles:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Selected user is not authorized "
                    "to conduct interviews."
                ),
            )


        if interviewer.company_id != company.id:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Interviewer does not belong "
                    "to this organization."
                ),
            )

        return await self.interview_repository.create(
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
        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        return await (
            self.interview_repository.get_by_company_id(
                company_id=company.id,
                skip=skip,
                limit=limit,
            )
        )

    # ============================================================
    # GET SINGLE ORGANIZATION INTERVIEW
    # ============================================================

    async def get_interview(
        self,
        user_id: UUID,
        interview_id: UUID,
    ):
        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        interview = await (
            self.interview_repository.get_by_id(
                interview_id=interview_id,
                company_id=company.id,
            )
        )

        if interview is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
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
        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        interview = await (
            self.interview_repository.get_by_id(
                interview_id=interview_id,
                company_id=company.id,
            )
        )

        if interview is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Interview not found.",
            )

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

        return await self.interview_repository.update(interview)

    # ============================================================
    # UPDATE INTERVIEW STATUS
    # ============================================================

    async def update_interview_status(
        self,
        user_id: UUID,
        interview_id: UUID,
        status: str,
    ):
        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        interview = await (
            self.interview_repository.get_by_id(
                interview_id=interview_id,
                company_id=company.id,
            )
        )

        if interview is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Interview not found.",
            )

        allowed_statuses = {
            "scheduled",
            "completed",
            "cancelled",
            "rescheduled",
            "no_show",
        }

        if status not in allowed_statuses:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid interview status. "
                    "Allowed values: scheduled, completed, "
                    "cancelled, rescheduled, no_show."
                ),
            )

        interview.status = status

        return await self.interview_repository.update(interview)

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
        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        interview = await (
            self.interview_repository.get_by_id(
                interview_id=interview_id,
                company_id=company.id,
            )
        )

        if interview is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Interview not found.",
            )

        if rating is not None:
            interview.rating = rating

        if feedback is not None:
            interview.feedback = feedback

        if recommendation is not None:
            interview.recommendation = recommendation

        if notes is not None:
            interview.notes = notes

        return await self.interview_repository.update(interview)

    # ============================================================
    # GET AVAILABLE INTERVIEWERS
    # ============================================================

    async def get_available_interviewers(
        self,
        user_id: UUID,
    ):
        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        return await (
            self.interview_repository.get_available_interviewers(
                company_id=company.id,
            )
        )

    # ============================================================
    # DELETE INTERVIEW
    # ============================================================

    async def delete_interview(
        self,
        user_id: UUID,
        interview_id: UUID,
    ):
        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        interview = await (
            self.interview_repository.get_by_id(
                interview_id=interview_id,
                company_id=company.id,
            )
        )

        if interview is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Interview not found.",
            )

        await self.interview_repository.delete(interview)

        return None
