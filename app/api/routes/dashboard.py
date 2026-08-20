from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_admin
from app.database.database import get_db
from app.models.user import User
from ...services.dashboard_service import DashboardService
from app.schemas.dashboard import (
    AdminSkillHubDashboardResponse,
    StudentSkillHubDashboardResponse,
)
from app.api.dependencies import (
    get_current_admin,
    get_current_user,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/admin/skillhub",
    response_model=AdminSkillHubDashboardResponse,
)
async def get_admin_skillhub_dashboard(
    current_user: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db),
):
    """
    Get SkillHub dashboard statistics for admin.
    """

    service = DashboardService(session)

    return await service.get_admin_skillhub_dashboard()
@router.get(
    "/student/skillhub",
    response_model=StudentSkillHubDashboardResponse,
)
async def get_student_skillhub_dashboard(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get SkillHub dashboard for the logged-in student.
    """

    service = DashboardService(session)

    return await service.get_student_skillhub_dashboard(
        current_user.id
    )