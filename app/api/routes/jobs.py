from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.company import Company
from app.models.job import Job
from app.models.user import User
from app.schemas.job import (
    JobCreate,
    JobResponse,
    JobUpdate,
)
from app.services.job_service import JobService


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


# ============================================================
# CREATE JOB
# ============================================================

@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_job(
    data: JobCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Create a job posted by the current user.
    """

    if data.company_id is not None:
        company = await session.get(
            Company,
            data.company_id,
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found.",
            )

    job = Job(
        company_id=data.company_id,
        posted_by=current_user.id,
        title=data.title,
        company_name=data.company_name,
        location=data.location,
        job_type=data.job_type,
        experience=data.experience,
        salary=data.salary,
        skills=data.skills,
        description=data.description,
        apply_email=data.apply_email,
        applicants=0,
        status=data.status,
    )

    service = JobService(session)

    created_job = await service.create_job(job)

    return JobResponse.model_validate(created_job)


# ============================================================
# GET OPEN JOBS
# ============================================================

@router.get(
    "",
    response_model=list[JobResponse],
)
async def get_jobs(
    company_id: UUID | None = Query(default=None),
    title: str | None = Query(default=None),
    location: str | None = Query(default=None),
    job_status: str | None = Query(
        default=None,
        alias="status",
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get jobs with optional filters.
    """

    service = JobService(session)

    if company_id is not None:
        jobs = await service.get_by_company_id(
            company_id,
            skip=skip,
            limit=limit,
        )

    elif title is not None:
        jobs = await service.get_by_title(
            title,
            skip=skip,
            limit=limit,
        )

    elif location is not None:
        jobs = await service.get_by_location(
            location,
            skip=skip,
            limit=limit,
        )

    elif job_status is not None:
        jobs = await service.get_by_status(
            job_status,
            skip=skip,
            limit=limit,
        )

    else:
        jobs = await service.get_open_jobs(
            skip=skip,
            limit=limit,
        )

    return [
        JobResponse.model_validate(job)
        for job in jobs
    ]


# ============================================================
# GET MY POSTED JOBS
# ============================================================

@router.get(
    "/me",
    response_model=list[JobResponse],
)
async def get_my_jobs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get jobs posted by the current user.
    """

    service = JobService(session)

    jobs = await service.get_by_posted_by(
        current_user.id,
        skip=skip,
        limit=limit,
    )

    return [
        JobResponse.model_validate(job)
        for job in jobs
    ]


# ============================================================
# GET JOB BY ID
# ============================================================

@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
async def get_job_by_id(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get a job by UUID.
    """

    service = JobService(session)

    job = await service.get_by_id(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    return JobResponse.model_validate(job)


# ============================================================
# UPDATE JOB
# ============================================================

@router.put(
    "/{job_id}",
    response_model=JobResponse,
)
async def update_job(
    job_id: UUID,
    data: JobUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Update a job belonging to the current user.
    """

    service = JobService(session)

    job = await service.get_by_id(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    if job.posted_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this job.",
        )

    if data.company_id is not None:
        company = await session.get(
            Company,
            data.company_id,
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found.",
            )

        job.company_id = data.company_id

    if data.title is not None:
        job.title = data.title

    if data.company_name is not None:
        job.company_name = data.company_name

    if data.location is not None:
        job.location = data.location

    if data.job_type is not None:
        job.job_type = data.job_type

    if data.experience is not None:
        job.experience = data.experience

    if data.salary is not None:
        job.salary = data.salary

    if data.skills is not None:
        job.skills = data.skills

    if data.description is not None:
        job.description = data.description

    if data.apply_email is not None:
        job.apply_email = data.apply_email

    if data.status is not None:
        job.status = data.status

    updated_job = await service.update_job(job)

    return JobResponse.model_validate(updated_job)


# ============================================================
# DELETE JOB
# ============================================================

@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Delete a job belonging to the current user.
    """

    service = JobService(session)

    job = await service.get_by_id(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    if job.posted_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this job.",
        )

    await service.delete_job(job)

    return None