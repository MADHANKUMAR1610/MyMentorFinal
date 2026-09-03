from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.database.database import get_db
from app.api.dependencies import get_current_user
from app.models.job import Job
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.job_application import (
    JobApplicationStatusUpdate,
    JobApplicationResponse,
)
from app.schemas.organization_job_details import (
    OrganizationJobDetailsResponse,
)
from app.services.job_application_service import (
    JobApplicationService,
)
from app.schemas.organization import OrganizationResponse, OrganizationUpdate
from app.services.organization_service import OrganizationService
from app.schemas.organization_dashboard import (
    OrganizationDashboardResponse,
)
from app.schemas.organization_job_summary import (
    OrganizationJobSummaryResponse,
)
from app.services.organization_dashboard_service import (
    OrganizationDashboardService,
)
from app.schemas.organization_job import (
    OrganizationJobCreate,
    OrganizationJobDraftCreate,
    OrganizationJobResponse,
    OrganizationJobUpdate,
)
from app.schemas.organization_ats_config import (
    OrganizationATSConfigUpdate,
    OrganizationATSConfigResponse,
)
from app.schemas.organization_job_list import OrganizationJobListResponse
from app.services.organization_ats_config_service import (
    OrganizationATSConfigService,
)
from app.services.organization_job_service import (
    OrganizationJobService,
)
router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.get(
    "/me",
    response_model=OrganizationResponse,
)
async def get_my_organization(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationService(db)

    return await service.get_my_organization(
        current_user.id
    )
@router.put(
    "/me",
    response_model=OrganizationResponse,
)
async def update_my_organization(
    data: OrganizationUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationService(db)

    return await service.update_my_organization(
        current_user.id,
        data,
    )
@router.get(
    "/me/jobs",
    response_model=list[OrganizationJobResponse],
)
async def get_my_jobs(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationJobService(db)

    return await service.get_my_jobs_full(
        current_user.id
    )
@router.post(
    "/me/jobs",
    response_model=OrganizationJobResponse,
    status_code=201,
)
async def create_my_job(
    data: OrganizationJobCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationJobService(db)

    return await service.create_job(
        current_user.id,
        data,
    )
@router.post(
    "/me/jobs/draft",
    response_model=OrganizationJobResponse,
    status_code=201,
)
async def save_job_draft(
    data: OrganizationJobDraftCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationJobService(db)

    return await service.save_draft(
        current_user.id,
        data,
    )
# ============================================================
# JOB SUMMARY
# ============================================================

@router.get(
    "/me/jobs/summary",
    response_model=OrganizationJobSummaryResponse,
)
async def get_my_job_summary(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get job statistics for the current user's organization.
    """

    service = OrganizationJobService(db)

    return await service.get_job_summary(
        current_user.id
    )
@router.get(
    "/me/jobs/{job_id}",
    response_model=OrganizationJobResponse,
)
async def get_my_job(
    job_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationJobService(db)

    return await service.get_job(
        current_user.id,
        job_id,
    )
@router.put(
    "/me/jobs/{job_id}",
    response_model=OrganizationJobResponse,
)
async def update_my_job(
    job_id: UUID,
    data: OrganizationJobUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationJobService(db)

    return await service.update_job(
        current_user.id,
        job_id,
        data,
    )
@router.get(
    "/me/jobslist",
    response_model=OrganizationJobListResponse,
)
async def get_my_jobs_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    status: str | None = Query(None),

    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationJobService(db)

    return await service.get_my_jobs_list(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        search=search,
        status=status,
    )# ============================================================
# ATS CONFIGURATION
# ============================================================

@router.get(
    "/me/ats-config",
    response_model=OrganizationATSConfigResponse,
)
async def get_my_ats_config(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationATSConfigService(db)

    return await service.get_config(
        current_user.id
    )
# ============================================================
# MOVE APPLICATION
# ============================================================

@router.put(
    "/me/jobs/{job_id}/applications/{application_id}/move",
    response_model=JobApplicationResponse,
)
async def move_job_application(
    job_id: UUID,
    application_id: UUID,
    data: JobApplicationStatusUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Move a candidate to another recruitment stage.
    """

    # --------------------------------------------------------
    # Find organization
    # --------------------------------------------------------

    organization_repository = OrganizationRepository(
        db
    )

    organization = await (
        organization_repository
        .get_by_admin_user_id(
            current_user.id
        )
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found for this user.",
        )

    # --------------------------------------------------------
    # Verify job belongs to organization
    # --------------------------------------------------------

    job = await db.get(
        Job,
        job_id,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    if job.company_id != organization.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this job.",
        )

    # --------------------------------------------------------
    # Get application BEFORE changing anything
    # --------------------------------------------------------

    service = JobApplicationService(
        db
    )

    application = await (
        service.repository
        .get_organization_application(
            application_id=application_id,
            company_id=organization.id,
        )
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found.",
        )

    # --------------------------------------------------------
    # Verify application belongs to this job
    # --------------------------------------------------------

    if application.job_id != job_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application does not belong to this job.",
        )

    # --------------------------------------------------------
    # Update + Audit Log
    # --------------------------------------------------------

    application = await (
        service.update_organization_application_status(
            application_id=application_id,
            company_id=organization.id,
            new_status=data.status,
            performed_by_user_id=current_user.id,
            performed_by_name=(
                current_user.name
                or "Organization Admin"
            ),
        )
    )

    return JobApplicationResponse.model_validate(
        application
    )
# ============================================================
# COMPLETE JOB DETAILS
# ============================================================

@router.get(
    "/me/jobs/{job_id}/details",
    response_model=OrganizationJobDetailsResponse,
)
async def get_job_details(
    job_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationJobService(db)

    return await service.get_job_details(
        user_id=current_user.id,
        job_id=job_id,
    )
@router.put(
    "/me/ats-config",
    response_model=OrganizationATSConfigResponse,
)
async def update_my_ats_config(
    data: OrganizationATSConfigUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationATSConfigService(db)

    return await service.update_config(
        current_user.id,
        data,
    )