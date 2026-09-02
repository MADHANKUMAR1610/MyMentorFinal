from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.repositories.job_repository import JobRepository


class JobService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.repository = JobRepository(
            session
        )

    # ============================================================
    # GET BY ID
    # ============================================================

    async def get_by_id(
        self,
        job_id: UUID,
    ) -> Job | None:

        return await self.repository.get_by_id(
            job_id
        )

    # ============================================================
    # GET BY COMPANY
    # ============================================================

    async def get_by_company_id(
        self,
        company_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Job]:

        return await self.repository.get_by_company_id(
            company_id,
            skip=skip,
            limit=limit,
        )

    # ============================================================
    # GET BY POSTED USER
    # ============================================================

    async def get_by_posted_by(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Job]:

        return await self.repository.get_by_posted_by(
            user_id,
            skip=skip,
            limit=limit,
        )

    # ============================================================
    # GET BY STATUS
    # ============================================================

    async def get_by_status(
        self,
        status: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Job]:

        return await self.repository.get_by_status(
            status,
            skip=skip,
            limit=limit,
        )

    # ============================================================
    # GET ACTIVE JOBS
    # ============================================================

    async def get_open_jobs(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Job]:

        return await self.repository.get_open_jobs(
            skip=skip,
            limit=limit,
        )

    # ============================================================
    # GET BY TITLE
    # ============================================================

    async def get_by_title(
        self,
        title: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Job]:

        return await self.repository.get_by_title(
            title,
            skip=skip,
            limit=limit,
        )

    # ============================================================
    # GET BY LOCATION
    # ============================================================

    async def get_by_location(
        self,
        location: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Job]:

        return await self.repository.get_by_location(
            location,
            skip=skip,
            limit=limit,
        )

    # ============================================================
    # CREATE JOB
    # ============================================================

    async def create_job(
        self,
        job: Job,
    ) -> Job:

        return await self.repository.create(
            job
        )

    # ============================================================
    # UPDATE JOB
    # ============================================================

    async def update_job(
        self,
        job: Job,
    ) -> Job:

        return await self.repository.update(
            job
        )

    # ============================================================
    # DELETE JOB
    # ============================================================

    async def delete_job(
        self,
        job: Job,
    ) -> None:

        await self.repository.delete(
            job
        )