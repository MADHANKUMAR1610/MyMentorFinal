from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.database.database import get_db
from app.api.dependencies import get_current_user

from app.schemas.organization import OrganizationResponse, OrganizationUpdate
from app.services.organization_service import OrganizationService
from app.schemas.organization_dashboard import (
    OrganizationDashboardResponse,
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
    "/me/dashboard",
    response_model=OrganizationDashboardResponse,
)
async def get_my_dashboard(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationDashboardService(db)

    return await service.get_my_dashboard(
        current_user.id
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

    return await service.get_my_jobs(
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
