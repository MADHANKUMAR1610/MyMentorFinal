from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job


class OrganizationJobRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_jobs_by_company_id(
        self,
        company_id: UUID,
    ) -> list[Job]:

        result = await self.db.execute(
            select(Job)
            .where(Job.company_id == company_id)
            .order_by(Job.created_at.desc())
        )

        return list(result.scalars().all())

    async def get_by_id(
        self,
        job_id: UUID,
        company_id: UUID,
    ) -> Job | None:

        result = await self.db.execute(
            select(Job).where(
                Job.id == job_id,
                Job.company_id == company_id,
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        company_id: UUID,
        posted_by: UUID,
        data: dict,
    ) -> Job:

        job = Job(
            company_id=company_id,
            posted_by=posted_by,
            company_name=data["company_name"],
            title=data["title"],
            location=data.get("location"),
            job_type=data.get("job_type", "Full-time"),
            experience=data.get("experience"),
            salary=data.get("salary"),
            skills=data.get("skills", []),
            description=data["description"],
            apply_email=data.get("apply_email"),
            applicants=0,
            status="open",
        )

        self.db.add(job)

        await self.db.commit()
        await self.db.refresh(job)

        return job
    async def update(
        self,
        job: Job,
        data: dict,
    ) -> Job:

        for field, value in data.items():
            if value is not None:
                setattr(job, field, value)

        await self.db.commit()
        await self.db.refresh(job)

        return job
    async def delete(
        self,
        job: Job,
    ) -> None:

        await self.db.delete(job)
        await self.db.commit()

    async def update_status(
        self,
        job: Job,
        status: str,
    ) -> Job:

        job.status = status

        await self.db.commit()
        await self.db.refresh(job)

        return job