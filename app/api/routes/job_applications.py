from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.job import Job
from app.models.job_application import JobApplication
from app.models.user import User
from app.schemas.job_application import (
    JobApplicationCreate,
    JobApplicationResponse,
    JobApplicationUpdate,
)
from app.services.job_application_service import (
    JobApplicationService,
)


router = APIRouter(
    prefix="/job-applications",
    tags=["Job Applications"],
)


# ============================================================
# CREATE JOB APPLICATION
# ============================================================

@router.post(
    "",
    response_model=JobApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_job_application(
    data: JobApplicationCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Apply for a job as the currently authenticated user.
    """

    # Check job exists
    job = await session.get(
        Job,
        data.job_id,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    # Check job is open
    if job.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This job is no longer accepting applications.",
        )

    service = JobApplicationService(session)

    # Prevent duplicate application
    existing_application = (
        await service.get_by_job_and_user(
            data.job_id,
            current_user.id,
        )
    )

    if existing_application is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already applied for this job.",
        )

    application = JobApplication(
        job_id=data.job_id,
        applicant_user_id=current_user.id,
        name=data.name,
        email=data.email,
        phone=data.phone,
        experience=data.experience,
        cover_note=data.cover_note,
        resume_link=data.resume_link,
        status="submitted",
    )

    created_application = (
        await service.create_application(
            application
        )
    )

    # Increase applicant count
    job.applicants += 1

    await session.flush()

    return JobApplicationResponse.model_validate(
        created_application
    )


# ============================================================
# GET MY APPLICATIONS
# ============================================================

@router.get(
    "/me",
    response_model=list[JobApplicationResponse],
)
async def get_my_job_applications(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get job applications submitted by the current user.
    """

    service = JobApplicationService(session)

    applications = (
        await service.get_by_applicant_user_id(
            current_user.id,
            skip=skip,
            limit=limit,
        )
    )

    return [
        JobApplicationResponse.model_validate(
            application
        )
        for application in applications
    ]


# ============================================================
# GET APPLICATION BY ID
# ============================================================

@router.get(
    "/{application_id}",
    response_model=JobApplicationResponse,
)
async def get_job_application_by_id(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get a job application by ID.
    """

    service = JobApplicationService(session)

    application = await service.get_by_id(
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found.",
        )

    if application.applicant_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this application.",
        )

    return JobApplicationResponse.model_validate(
        application
    )


# ============================================================
# UPDATE MY APPLICATION
# ============================================================

@router.put(
    "/{application_id}",
    response_model=JobApplicationResponse,
)
async def update_job_application(
    application_id: UUID,
    data: JobApplicationUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Update a job application belonging to the current user.
    """

    service = JobApplicationService(session)

    application = await service.get_by_id(
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found.",
        )

    if application.applicant_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this application.",
        )

    if data.name is not None:
        application.name = data.name

    if data.email is not None:
        application.email = data.email

    if data.phone is not None:
        application.phone = data.phone

    if data.experience is not None:
        application.experience = data.experience

    if data.cover_note is not None:
        application.cover_note = data.cover_note

    if data.resume_link is not None:
        application.resume_link = data.resume_link

    # Applicant should not change application status.
    updated_application = (
        await service.update_application(
            application
        )
    )

    return JobApplicationResponse.model_validate(
        updated_application
    )


# ============================================================
# DELETE MY APPLICATION
# ============================================================

@router.delete(
    "/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_job_application(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Delete a job application belonging to the current user.
    """

    service = JobApplicationService(session)

    application = await service.get_by_id(
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found.",
        )

    if application.applicant_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this application.",
        )

    job = await session.get(
        Job,
        application.job_id,
    )

    await service.delete_application(
        application
    )

    # Decrease applicant count
    if job is not None and job.applicants > 0:
        job.applicants -= 1

    await session.flush()

    return None