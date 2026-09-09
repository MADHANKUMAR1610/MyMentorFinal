# app/api/routes/job_applications.py

from uuid import UUID
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from fastapi import Depends, HTTPException, Query, APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

from app.database.database import get_db
from app.api.dependencies import get_current_user

from app.models.user import User
from app.models.job_application import JobApplication

from app.schemas.job_application import (
    JobApplicationCreate,
    JobApplicationUpdate,
    JobApplicationResponse,
    JobApplicationStatusUpdate,
    JobApplicationStatsResponse,
)

from app.services.job_application_service import JobApplicationService
from app.services.job_service import JobService


router = APIRouter(
    prefix="/job-applications",
    tags=["Job Applications"],
)


# ------------------------------------------------------------------
# Dependencies
# ------------------------------------------------------------------


async def get_job_application_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobApplicationService:
    return JobApplicationService(db)


async def get_job_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobService:
    return JobService(db)


# ------------------------------------------------------------------
# Create Application
# ------------------------------------------------------------------


@router.post(
    "",
    response_model=JobApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_application(
    data: JobApplicationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    application_service: Annotated[
        JobApplicationService,
        Depends(get_job_application_service),
    ],
    job_service: Annotated[
        JobService,
        Depends(get_job_service),
    ],
):
    """
    Submit an application for a job.

    The service is responsible for:
    - Email normalization
    - Duplicate application validation
    - Resume validation
    - Initial status assignment
    - Application creation
    """

    job = await job_service.get_by_id(data.job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if hasattr(job, "is_active") and not job.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This job is no longer accepting applications",
        )

    application = JobApplication(
       job_id=data.job_id,
       applicant_user_id=current_user.id,
       name=data.name,
       email=data.email,
       phone=data.phone,
       experience=data.experience,
       cover_note=data.cover_note,
       resume_file_id=data.resume_file_id,
       resume_source=data.resume_source,
       resume_link=str(data.resume_link) if data.resume_link else None,
    )

    application = await application_service.submit_application(application)

    return application

# ------------------------------------------------------------------
# Get My Applications
# ------------------------------------------------------------------


@router.get(
    "/me",
    response_model=list[JobApplicationResponse],
)
async def get_my_applications(
    current_user: Annotated[User, Depends(get_current_user)],
    application_service: Annotated[
        JobApplicationService,
        Depends(get_job_application_service),
    ],
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of records to return",
    ),
):
    """
    Get applications submitted by the authenticated user.
    """

    applications = await application_service.get_by_applicant_user_id(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    return applications

# ------------------------------------------------------------------
# Recruiter: Get Applications By Status
# ------------------------------------------------------------------


@router.get(
    "/recruiter/status",
    response_model=list[JobApplicationResponse],
)
async def get_applications_by_status(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    application_service: Annotated[
        JobApplicationService,
        Depends(get_job_application_service),
    ],
    application_status: str = Query(
        ...,
        alias="status",
        description="Application status",
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of records to return",
    ),
):
    """
    Get applications by status.

    Example:
    GET /job-applications/recruiter/status?status=screening
    """

    applications = await application_service.get_by_status(
        application_status=application_status,
        skip=skip,
        limit=limit,
    )

    return applications
# ------------------------------------------------------------------
# Get Application By ID
# ------------------------------------------------------------------


@router.get(
    "/{application_id}",
    response_model=JobApplicationResponse,
)
async def get_application_by_id(
    application_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    application_service: Annotated[
        JobApplicationService,
        Depends(get_job_application_service),
    ],
):
    """
    Get one application.

    Applicants can access only their own applications.
    Recruiter/company authorization should be handled separately
    if recruiter access is required.
    """

    application = await application_service.get_by_id(
        application_id=application_id,
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    if application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this application",
        )

    return application


# ------------------------------------------------------------------
# Update My Application
# ------------------------------------------------------------------


@router.patch(
    "/{application_id}",
    response_model=JobApplicationResponse,
)
async def update_application(
    application_id: UUID,
    data: JobApplicationUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    application_service: Annotated[
        JobApplicationService,
        Depends(get_job_application_service),
    ],
):
    """
    Update an application owned by the authenticated user.

    Status changes are not allowed through this endpoint.
    Use the recruiter status endpoint for status updates.
    """

    application = await application_service.get_by_id(
        application_id=application_id,
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    if application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this application",
        )

    if application.status in {
        "selected",
        "rejected",
        "withdrawn",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Applications with selected, rejected, or withdrawn "
                "status cannot be updated"
            ),
        )

    update_data = data.model_dump(
        exclude_unset=True,
    )

    if "applicant_email" in update_data:
        update_data["applicant_email"] = (
            str(update_data["applicant_email"])
            .strip()
            .lower()
        )

    if "resume_link" in update_data:
        update_data["resume_link"] = (
            str(update_data["resume_link"])
            if update_data["resume_link"]
            else None
        )

    updated_application = await application_service.update_application(
        application_id=application_id,
        user_id=current_user.id,
        update_data=update_data,
    )

    if not updated_application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return updated_application


# ------------------------------------------------------------------
# Withdraw My Application
# ------------------------------------------------------------------


@router.delete(
    "/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def withdraw_application(
    application_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    application_service: Annotated[
        JobApplicationService,
        Depends(get_job_application_service),
    ],
):
    """
    Withdraw an application owned by the authenticated user.

    This should preferably perform a soft delete by changing
    the application status to withdrawn.
    """

    application = await application_service.get_by_id(
        application_id=application_id,
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    if application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to withdraw this application",
        )

    if application.status in {
        "selected",
        "rejected",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Selected or rejected applications cannot be withdrawn"
            ),
        )

    await application_service.update_status(
        application_id=application_id,
        new_status="withdrawn",
        changed_by_user_id=current_user.id,
    )

    return None



# ------------------------------------------------------------------
# Recruiter: Get Applications By Company
# ------------------------------------------------------------------


@router.get(
    "/recruiter/company/{company_id}",
    response_model=list[JobApplicationResponse],
)
async def get_applications_by_company(
    company_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    application_service: Annotated[
        JobApplicationService,
        Depends(get_job_application_service),
    ],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    """
    Get all applications for jobs belonging to a company.

    Add a recruiter/company membership check before returning data.
    """

    applications = await application_service.get_by_company_id(
        company_id=company_id,
        skip=skip,
        limit=limit,
    )

    return applications


# ------------------------------------------------------------------
# Recruiter: Update Application Status
# ------------------------------------------------------------------


@router.patch(
    "/recruiter/{application_id}/status",
    response_model=JobApplicationResponse,
)
async def update_application_status(
    application_id: UUID,
    data: JobApplicationStatusUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    application_service: Annotated[
        JobApplicationService,
        Depends(get_job_application_service),
    ],
):
    """
    Recruiter updates the status of an application.

    Add organization/company authorization before calling the service.
    """

    application = await application_service.get_by_id(
        application_id=application_id,
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    updated_application = await application_service.update_status(
        application_id=application_id,
        new_status=data.status,
        changed_by_user_id=current_user.id,
        notes=getattr(data, "notes", None),
    )

    if not updated_application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return updated_application


# ------------------------------------------------------------------
# Recruiter: Application Statistics
# ------------------------------------------------------------------


@router.get(
    "/recruiter/stats/{company_id}",
    response_model=JobApplicationStatsResponse,
)
async def get_application_stats(
    company_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    application_service: Annotated[
        JobApplicationService,
        Depends(get_job_application_service),
    ],
):
    """
    Get application statistics for a company.

    The service should return a dictionary/object matching
    JobApplicationStatsResponse.
    """

    stats = await application_service.get_statistics(
        company_id=company_id,
    )

    return stats