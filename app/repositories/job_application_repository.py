from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_application import JobApplication
from app.repositories.base import BaseRepository


class JobApplicationRepository(
    BaseRepository[JobApplication]
):
    """
    Repository responsible for JobApplication
    database operations.

    Business rules belong in the service layer.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(JobApplication, session)

    async def get_by_job_id(
        self,
        job_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JobApplication]:
        """
        Get applications submitted for a specific job.
        """

        result = await self.session.execute(
            select(JobApplication)
            .where(
                JobApplication.job_id == job_id
            )
            .order_by(
                JobApplication.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_applicant_user_id(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JobApplication]:
        """
        Get applications submitted by a specific user.
        """

        result = await self.session.execute(
            select(JobApplication)
            .where(
                JobApplication.applicant_user_id == user_id
            )
            .order_by(
                JobApplication.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_email(
        self,
        email: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JobApplication]:
        """
        Get applications using applicant email.
        """

        result = await self.session.execute(
            select(JobApplication)
            .where(
                JobApplication.email == email
            )
            .order_by(
                JobApplication.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_status(
        self,
        status: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JobApplication]:
        """
        Get applications by status.
        """

        result = await self.session.execute(
            select(JobApplication)
            .where(
                JobApplication.status == status
            )
            .order_by(
                JobApplication.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_job_and_user(
        self,
        job_id: UUID,
        user_id: UUID,
    ) -> Optional[JobApplication]:
        """
        Get a user's application for a specific job.
        """

        result = await self.session.execute(
            select(JobApplication).where(
                JobApplication.job_id == job_id,
                JobApplication.applicant_user_id == user_id,
            )
        )

        return result.scalar_one_or_none()