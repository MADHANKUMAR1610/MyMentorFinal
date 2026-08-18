from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[Job]):
    """
    Repository responsible for Job database operations.

    Business rules belong in the service layer.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Job, session)

    async def get_by_company_id(
        self,
        company_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Job]:
        """
        Get jobs belonging to a company.
        """

        result = await self.session.execute(
            select(Job)
            .where(Job.company_id == company_id)
            .order_by(Job.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_posted_by(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Job]:
        """
        Get jobs posted by a user.
        """

        result = await self.session.execute(
            select(Job)
            .where(Job.posted_by == user_id)
            .order_by(Job.created_at.desc())
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
    ) -> list[Job]:
        """
        Get jobs by status.
        """

        result = await self.session.execute(
            select(Job)
            .where(Job.status == status)
            .order_by(Job.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_open_jobs(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Job]:
        """
        Get currently open jobs.
        """

        result = await self.session.execute(
            select(Job)
            .where(Job.status == "open")
            .order_by(Job.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_title(
        self,
        title: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Job]:
        """
        Get jobs matching an exact title.
        """

        result = await self.session.execute(
            select(Job)
            .where(Job.title == title)
            .order_by(Job.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_location(
        self,
        location: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Job]:
        """
        Get jobs by location.
        """

        result = await self.session.execute(
            select(Job)
            .where(Job.location == location)
            .order_by(Job.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())