from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db

from app.schemas.organization_analytics import (
    OrganizationRecruitmentAnalyticsResponse,
)

from app.services.analytics_service import (
    OrganizationAnalyticsService,
)


router = APIRouter(
    prefix="/organizations/me/analytics",
    tags=["Organization Analytics"],
)


# ============================================================
# GET ORGANIZATION RECRUITMENT ANALYTICS
# ============================================================

@router.get(
    "/recruitment",
    response_model=OrganizationRecruitmentAnalyticsResponse,
)
async def get_recruitment_analytics(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get recruitment analytics for the current user's organization.
    """

    service = OrganizationAnalyticsService(db)

    analytics = await service.get_recruitment_analytics(
        current_user.id
    )

    return analytics
# ============================================================
# GET APPLICATION TREND
# ============================================================

@router.get(
    "/recruitment/application-trend",
)
async def get_application_trend(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get daily application trend
    for the current user's organization.
    """

    service = OrganizationAnalyticsService(db)

    return await service.get_application_trend(
        current_user.id
    )
# ============================================================
# GET RECRUITMENT FUNNEL
# ============================================================

@router.get(
    "/recruitment/funnel",
)
async def get_recruitment_funnel(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get recruitment funnel statistics
    for the current user's organization.
    """

    service = OrganizationAnalyticsService(db)

    return await service.get_recruitment_funnel(
        current_user.id
    )
# ============================================================
# GET INTERVIEW ANALYTICS
# ============================================================

@router.get(
    "/recruitment/interviews",
)
async def get_interview_analytics(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get interview statistics
    for the current user's organization.
    """

    service = OrganizationAnalyticsService(db)

    return await service.get_interview_analytics(
        current_user.id
    )
# ============================================================
# GET JOB-WISE RECRUITMENT ANALYTICS
# ============================================================

@router.get(
    "/recruitment/jobs",
)
async def get_job_wise_recruitment_analytics(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get recruitment analytics for each job
    in the current user's organization.
    """

    service = OrganizationAnalyticsService(db)

    return await service.get_job_wise_recruitment_analytics(
        current_user.id
    )
# ============================================================
# GET HIRING RATE
# ============================================================

@router.get(
    "/recruitment/hiring-rate",
)
async def get_hiring_rate(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get hiring rate for the current user's organization.
    """

    service = OrganizationAnalyticsService(db)

    return await service.get_hiring_rate(
        current_user.id
    )
# ============================================================
# GET AVERAGE TIME TO HIRE
# ============================================================

@router.get(
    "/recruitment/average-time-to-hire",
)
async def get_average_time_to_hire(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the average time taken to hire candidates
    for the current user's organization.
    """

    service = OrganizationAnalyticsService(db)

    return await service.get_average_time_to_hire(
        current_user.id
    )
# ============================================================
# GET RECRUITMENT DASHBOARD SUMMARY
# ============================================================

@router.get(
    "/recruitment/dashboard",
)
async def get_recruitment_dashboard(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get complete recruitment analytics
    dashboard summary for the current organization.
    """

    service = OrganizationAnalyticsService(db)

    return await service.get_recruitment_dashboard(
        current_user.id
    )