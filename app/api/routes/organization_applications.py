from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.job import Job

from app.repositories.organization_repository import (
    OrganizationRepository,
)

from app.schemas.job_application import (
    JobApplicationResponse,
    JobApplicationStatusUpdate,
    JobApplicationStatsResponse,
    OrganizationApplicationStatsResponse,
)

from app.services.job_application_service import (
    JobApplicationService,
)

from app.services.organization_job_service import (
    OrganizationJobService,
    
)

from app.schemas.organization_job import (
    OrganizationJobResponse,
    OrganizationJobStatusUpdate,
)
from fastapi import APIRouter

router = APIRouter(
    prefix="/organizations/me",
    tags=["Organization Applications"],
)


# ============================================================
# GET ALL ORGANIZATION APPLICATIONS
# ============================================================

@router.get(
    "/applications",
    response_model=list[JobApplicationResponse],
)
async def get_my_organization_applications(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    status: str | None = Query(
        default=None,
    ),
    name: str | None = Query(
        default=None,
    ),
    email: str | None = Query(
        default=None,
    ),
    job_id: UUID | None = Query(
        default=None,
    ),
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get applications belonging to the current user's
    organization with optional filters.
    """

    # --------------------------------------------------------
    # Find organization
    # --------------------------------------------------------

    organization_repository = OrganizationRepository(
        session
    )

    organization = (
        await organization_repository.get_by_admin_user_id(
            current_user.id
        )
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found for this user.",
        )

    # --------------------------------------------------------
    # Get filtered applications
    # --------------------------------------------------------

    service = JobApplicationService(session)

    applications = await service.get_by_company_id(
        organization.id,
        skip=skip,
        limit=limit,
        status=status,
        name=name,
        email=email,
        job_id=job_id,
    )

    # --------------------------------------------------------
    # Return response
    # --------------------------------------------------------

    return [
        JobApplicationResponse.model_validate(
            application
        )
        for application in applications
    ]
# ============================================================
# GET APPLICATIONS FOR ORGANIZATION JOB
# ============================================================

@router.get(
    "/jobs/{job_id}/applications",
    response_model=list[JobApplicationResponse],
)
async def get_job_applications_for_organization(
    job_id: UUID,
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get applications for a specific job belonging
    to the current user's organization.
    """

    # --------------------------------------------------------
    # Find organization
    # --------------------------------------------------------

    organization_repository = OrganizationRepository(
        session
    )

    organization = (
        await organization_repository.get_by_admin_user_id(
            current_user.id
        )
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found for this user.",
        )

    # --------------------------------------------------------
    # Check job exists
    # --------------------------------------------------------

    job = await session.get(
        Job,
        job_id,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    # --------------------------------------------------------
    # Check job belongs to organization
    # --------------------------------------------------------

    if job.company_id != organization.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this job.",
        )

    # --------------------------------------------------------
    # Get applications
    # --------------------------------------------------------

    service = JobApplicationService(session)

    applications = await service.get_by_job_id(
        job_id,
        skip=skip,
        limit=limit,
    )

    return [
        JobApplicationResponse.model_validate(
            application
        )
        for application in applications
    ]
# ============================================================
# GET ORGANIZATION APPLICATION STATISTICS
# ============================================================
@router.get(
    "/applications/stats",
    response_model=OrganizationApplicationStatsResponse,
)
async def get_my_organization_application_stats(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    organization_repository = OrganizationRepository(
        session
    )

    organization = (
        await organization_repository.get_by_admin_user_id(
            current_user.id
        )
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found for this user.",
        )

    service = JobApplicationService(session)

    return await service.get_organization_application_stats(
        organization.id
    )
# ============================================================
# GET ORGANIZATION APPLICATION BY ID
# ============================================================

@router.get(
    "/applications/{application_id}",
    response_model=JobApplicationResponse,
)
async def get_organization_application(
    application_id: UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get a specific job application belonging
    to the current user's organization.
    """

    # --------------------------------------------------------
    # Find organization
    # --------------------------------------------------------

    organization_repository = OrganizationRepository(
        session
    )

    organization = (
        await organization_repository.get_by_admin_user_id(
            current_user.id
        )
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found for this user.",
        )

    # --------------------------------------------------------
    # Get application belonging to organization
    # --------------------------------------------------------

    service = JobApplicationService(session)

    application = await service.get_organization_application(
        application_id,
        organization.id,
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found.",
        )

    return JobApplicationResponse.model_validate(
        application
    )


# ============================================================
# UPDATE APPLICATION STATUS
# ============================================================

@router.put(
    "/applications/{application_id}/status",
    response_model=JobApplicationResponse,
)
async def update_organization_application_status(
    application_id: UUID,
    data: JobApplicationStatusUpdate,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Update the status of an application belonging
    to the current user's organization.
    """

    # --------------------------------------------------------
    # Find organization
    # --------------------------------------------------------

    organization_repository = OrganizationRepository(
        session
    )

    organization = (
        await organization_repository.get_by_admin_user_id(
            current_user.id
        )
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found for this user.",
        )

    # --------------------------------------------------------
    # Update application status
    # --------------------------------------------------------

    service = JobApplicationService(session)

    application = (
        await service.update_organization_application_status(
            application_id=application_id,
            company_id=organization.id,
            new_status=data.status,
        )
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found.",
        )

    return JobApplicationResponse.model_validate(
        application
    )


# ============================================================
# DELETE ORGANIZATION JOB
# ============================================================

@router.delete(
    "/jobs/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_my_job(
    job_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a job belonging to the current user's organization.
    """

    service = OrganizationJobService(db)

    await service.delete_job(
        current_user.id,
        job_id,
    )

    return None


# ============================================================
# UPDATE ORGANIZATION JOB STATUS
# ============================================================

@router.put(
    "/jobs/{job_id}/status",
    response_model=OrganizationJobResponse,
)
async def update_my_job_status(
    job_id: UUID,
    data: OrganizationJobStatusUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the status of a job belonging
    to the current user's organization.
    """

    service = OrganizationJobService(db)

    return await service.update_job_status(
        current_user.id,
        job_id,
        data.status,
    )
# ============================================================
# DUPLICATE JOB
# ============================================================

@router.post(
    "/{job_id}/duplicate",
)
async def duplicate_job(
    job_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Duplicate an existing job
    for the current organization.
    """

    service = OrganizationJobService(db)

    return await service.duplicate_job(
        user_id=current_user.id,
        job_id=job_id,
    )
