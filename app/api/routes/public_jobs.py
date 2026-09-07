from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.models.job import Job
from app.schemas.public_job import (
    PublicJobListItem,
    PublicJobListResponse,
)


router = APIRouter(
    prefix="/public/jobs",
    tags=["Public Jobs"],
)


@router.get(
    "",
    response_model=PublicJobListResponse,
)
async def get_public_jobs(
    search: str | None = Query(
        default=None,
        description="Search by job title, company, location, or description",
    ),
    location: str | None = Query(default=None),
    job_type: str | None = Query(default=None),
    work_mode: str | None = Query(default=None),
    min_experience: int | None = Query(default=None, ge=0),
    max_experience: int | None = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """
    Get active jobs from all organizations.

    This endpoint is public and does not require authentication.
    """

    # --------------------------------------------------------
    # Base query
    # --------------------------------------------------------
    query = select(Job).where(
        Job.status == "active"
    )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------
    if search:
        search_pattern = f"%{search.strip()}%"

        query = query.where(
            or_(
                Job.title.ilike(search_pattern),
                Job.company_name.ilike(search_pattern),
                Job.location.ilike(search_pattern),
                Job.description.ilike(search_pattern),
            )
        )

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------
    if location:
        query = query.where(
            Job.location.ilike(f"%{location.strip()}%")
        )

    # --------------------------------------------------------
    # Job type
    # --------------------------------------------------------
    if job_type:
        query = query.where(
            Job.job_type == job_type
        )

    # --------------------------------------------------------
    # Work mode
    # --------------------------------------------------------
    if work_mode:
        query = query.where(
            Job.work_mode == work_mode
        )

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------
    if min_experience is not None:
        query = query.where(
            or_(
                Job.max_experience.is_(None),
                Job.max_experience >= min_experience,
            )
        )

    if max_experience is not None:
        query = query.where(
            or_(
                Job.min_experience.is_(None),
                Job.min_experience <= max_experience,
            )
        )

    # --------------------------------------------------------
    # Total count
    # --------------------------------------------------------
    count_query = select(
        func.count()
    ).select_from(
        query.order_by(None).subquery()
    )

    total = await session.scalar(count_query) or 0

    # --------------------------------------------------------
    # Pagination
    # --------------------------------------------------------
    skip = (page - 1) * page_size

    query = query.order_by(
        Job.created_at.desc()
    ).offset(skip).limit(page_size)

    result = await session.execute(query)

    jobs = result.scalars().all()

    total_pages = ceil(total / page_size) if total else 0

    return PublicJobListResponse(
        items=[
            PublicJobListItem.model_validate(job)
            for job in jobs
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )