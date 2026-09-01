from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db

from app.schemas.organization_dashboard import (
    OrganizationDashboardResponse,
)

from app.services.organization_dashboard_service import (
    OrganizationDashboardService,
)


router = APIRouter(
    prefix="/organizations/me",
    tags=["Organization Dashboard"],
)


# ============================================================
# GET ORGANIZATION ADMIN DASHBOARD
# ============================================================

@router.get(
    "/dashboard",
    response_model=OrganizationDashboardResponse,
)
async def get_organization_dashboard(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = OrganizationDashboardService(db)

    return await service.get_dashboard(
        current_user.id
    )