from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_current_admin,
    get_current_user,
)
from app.database.database import get_db
from app.models.user import User
from app.schemas.dashboard import (
    AdminDashboardResponse,
    StudentDashboardResponse,
)
from app.services.dashboard_service import (
    DashboardService,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@router.get(
    "/admin/skillhub",
    response_model=AdminDashboardResponse,
)
async def get_admin_skillhub_dashboard(
    current_user: User = Depends(
        get_current_admin
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = DashboardService(session)

    return await service.get_admin_dashboard()


# ============================================================
# STUDENT DASHBOARD
# ============================================================

@router.get(
    "/student/skillhub",
    response_model=StudentDashboardResponse,
)
async def get_student_skillhub_dashboard(
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = DashboardService(session)

    try:

        return await service.get_student_dashboard(
            current_user.id
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )