from math import ceil
from uuid import UUID

from fastapi import HTTPException
from fastapi import APIRouter, Depends, Query

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db

from app.models.job import Job
from app.models.job_application import JobApplication

from app.schemas.public_job import (
    PublicJobListItem,
    PublicJobListResponse,
    PublicJobDetailsResponse,
)


router = APIRouter(
    prefix="/public/jobs",
    tags=["Public Jobs"],
)


# ============================================================
# GET PUBLIC JOBS
# ============================================================

@router.get(
    "",
    response_model=PublicJobListResponse,
)
async def get_public_jobs(

    search: str | None = Query(
        default=None,
        description=(
            "Search by job title, company, "
            "location, or description"
        ),
    ),

    location: str | None = Query(
        default=None
    ),

    job_type: str | None = Query(
        default=None
    ),

    work_mode: str | None = Query(
        default=None
    ),

    min_experience: int | None = Query(
        default=None,
        ge=0,
    ),

    max_experience: int | None = Query(
        default=None,
        ge=0,
    ),

    page: int = Query(
        default=1,
        ge=1,
    ),

    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
    ),

    session: AsyncSession = Depends(
        get_db
    ),
):

    """
    Get active jobs from all organizations.

    This endpoint is public and does not require authentication.
    """

    # ========================================================
    # BASE QUERY
    # ========================================================

    query = select(Job).where(
        Job.status == "active"
    )

    # ========================================================
    # SEARCH
    # ========================================================

    if search:

        search_pattern = (
            f"%{search.strip()}%"
        )

        query = query.where(
            or_(
                Job.title.ilike(
                    search_pattern
                ),

                Job.company_name.ilike(
                    search_pattern
                ),

                Job.location.ilike(
                    search_pattern
                ),

                Job.description.ilike(
                    search_pattern
                ),
            )
        )

    # ========================================================
    # LOCATION
    # ========================================================

    if location:

        query = query.where(
            Job.location.ilike(
                f"%{location.strip()}%"
            )
        )

    # ========================================================
    # JOB TYPE
    # ========================================================

    if job_type:

        query = query.where(
            Job.job_type == job_type
        )

    # ========================================================
    # WORK MODE
    # ========================================================

    if work_mode:

        query = query.where(
            Job.work_mode == work_mode
        )

    # ========================================================
    # EXPERIENCE
    # ========================================================

    if min_experience is not None:

        query = query.where(
            or_(
                Job.max_experience.is_(None),
                Job.max_experience
                >= min_experience,
            )
        )

    if max_experience is not None:

        query = query.where(
            or_(
                Job.min_experience.is_(None),
                Job.min_experience
                <= max_experience,
            )
        )

    # ========================================================
    # TOTAL COUNT
    # ========================================================

    count_query = (
        select(func.count())
        .select_from(
            query
            .order_by(None)
            .subquery()
        )
    )

    total = (
        await session.scalar(
            count_query
        )
        or 0
    )

    # ========================================================
    # PAGINATION
    # ========================================================

    skip = (
        (page - 1)
        * page_size
    )

    query = (
        query
        .order_by(
            Job.created_at.desc()
        )
        .offset(skip)
        .limit(page_size)
    )

    result = await session.execute(
        query
    )

    jobs = result.scalars().all()

    # ========================================================
    # GET REAL APPLICANT COUNTS
    # ========================================================

    job_ids = [
        job.id
        for job in jobs
    ]

    applicant_count_map = {}

    if job_ids:

        applicant_result = (
            await session.execute(
                select(
                    JobApplication.job_id,
                    func.count(
                        JobApplication.id
                    ),
                )
                .where(
                    JobApplication.job_id.in_(
                        job_ids
                    )
                )
                .group_by(
                    JobApplication.job_id
                )
            )
        )

        applicant_count_map = {
            job_id: count
            for job_id, count
            in applicant_result.all()
        }

    # ========================================================
    # BUILD JOB ITEMS
    # ========================================================

    items = []

    for job in jobs:

        item = (
            PublicJobListItem
            .model_validate(job)
        )

        item.applicants = (
            applicant_count_map.get(
                job.id,
                0
            )
        )

        items.append(item)

    # ========================================================
    # TOTAL PAGES
    # ========================================================

    total_pages = (
        ceil(
            total / page_size
        )
        if total
        else 0
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return PublicJobListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# ============================================================
# GET PUBLIC JOB DETAILS
# ============================================================

@router.get(
    "/{job_id}",
    response_model=PublicJobDetailsResponse,
)
async def get_public_job_details(

    job_id: UUID,

    session: AsyncSession = Depends(
        get_db
    ),
):

    """
    Get one active job from any organization.

    This endpoint is public and does not require authentication.
    """

    query = select(Job).where(
        Job.id == job_id,
        Job.status == "active",
    )

    result = await session.execute(
        query
    )

    job = result.scalar_one_or_none()

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    # ========================================================
    # REAL APPLICANT COUNT
    # ========================================================

    applicant_count = await session.scalar(
        select(
            func.count(
                JobApplication.id
            )
        ).where(
            JobApplication.job_id == job.id
        )
    )

    job.applicants = (
        applicant_count or 0
    )

    return (
        PublicJobDetailsResponse
        .model_validate(job)
    )