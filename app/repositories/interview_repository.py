from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview import Interview
from app.models.user import User
from app.models.job_application import JobApplication
from app.models.job import Job


class InterviewRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # GET USER BY ID
    # ============================================================

    async def get_user_by_id(
        self,
        user_id: UUID,
    ) -> User | None:

        result = await self.db.execute(
            select(User)
            .where(
                User.id == user_id
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # GET APPLICATION BY ID FOR COMPANY
    # ============================================================

    async def get_application_by_id(
        self,
        application_id: UUID,
        company_id: UUID,
    ) -> JobApplication | None:

        result = await self.db.execute(
            select(JobApplication)
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                JobApplication.id == application_id,
                Job.company_id == company_id,
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # CREATE INTERVIEW
    # ============================================================

    async def create(
        self,
        *,
        company_id: UUID,
        application_id: UUID,
        interviewer_id: UUID,
        title: str,
        interview_type: str,
        scheduled_at: datetime,
        duration_minutes: int,
        mode: str,
        meeting_link: str | None,
        location: str | None,
        notes: str | None,
    ) -> Interview:

        interview = Interview(
            company_id=company_id,
            application_id=application_id,
            interviewer_id=interviewer_id,
            title=title,
            interview_type=interview_type,
            scheduled_at=scheduled_at,
            duration_minutes=duration_minutes,
            mode=mode,
            meeting_link=meeting_link,
            location=location,
            status="scheduled",
            notes=notes,
        )

        self.db.add(interview)

        await self.db.commit()
        await self.db.refresh(interview)

        return interview
    # ============================================================
    # GET ALL COMPANY INTERVIEWS
    # ============================================================

    async def get_by_company_id(
        self,
        company_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Interview]:

        result = await self.db.execute(
            select(Interview)
            .where(
                Interview.company_id == company_id
            )
            .order_by(
                Interview.scheduled_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())
    # ============================================================
    # GET INTERVIEW BY ID
    # ============================================================

    async def get_by_id(
        self,
        interview_id: UUID,
        company_id: UUID,
    ) -> Interview | None:

        result = await self.db.execute(
            select(Interview)
            .where(
                Interview.id == interview_id,
                Interview.company_id == company_id,
            )
        )

        return result.scalar_one_or_none()

    async def update(
        self,
        interview: Interview,
    ) -> Interview:

        await self.db.commit()
        await self.db.refresh(interview)

        return interview

    # ============================================================
    # UPDATE INTERVIEW FEEDBACK
    # ============================================================

    async def update_feedback(
        self,
        interview: Interview,
    ) -> Interview:

        await self.db.commit()
        await self.db.refresh(interview)

        return interview
    # ============================================================
# DELETE INTERVIEW
# ============================================================

    async def delete(
        self,
        interview: Interview,
    ) -> None:

        await self.db.delete(interview)

        await self.db.commit()