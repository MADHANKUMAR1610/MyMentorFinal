from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_company_admin
from app.database.database import get_db

from app.schemas.organization_analytics import (
    OrganizationRecruitmentAnalyticsResponse,
    RecruitmentDashboardResponse,
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
    current_user=Depends(
        get_current_company_admin
    ),
    db: AsyncSession = Depends(get_db),
):

    service = OrganizationAnalyticsService(db)

    return await (
        service.get_recruitment_analytics(
            current_user.company_id
        )
    )


# ============================================================
# GET APPLICATION TREND
# ============================================================

@router.get(
    "/recruitment/application-trend"
)
async def get_application_trend(
    current_user=Depends(
        get_current_company_admin
    ),
    db: AsyncSession = Depends(get_db),
):

    service = OrganizationAnalyticsService(db)

    return await (
        service.get_application_trend(
            current_user.company_id
        )
    )


# ============================================================
# GET RECRUITMENT FUNNEL
# ============================================================

@router.get(
    "/recruitment/funnel"
)
async def get_recruitment_funnel(
    current_user=Depends(
        get_current_company_admin
    ),
    db: AsyncSession = Depends(get_db),
):

    service = OrganizationAnalyticsService(db)

    return await (
        service.get_recruitment_funnel(
            current_user.company_id
        )
    )


# ============================================================
# GET INTERVIEW ANALYTICS
# ============================================================

@router.get(
    "/recruitment/interviews"
)
async def get_interview_analytics(
    current_user=Depends(
        get_current_company_admin
    ),
    db: AsyncSession = Depends(get_db),
):

    service = OrganizationAnalyticsService(db)

    return await (
        service.get_interview_analytics(
            current_user.company_id
        )
    )


# ============================================================
# GET JOB-WISE RECRUITMENT ANALYTICS
# ============================================================

@router.get(
    "/recruitment/jobs"
)
async def get_job_wise_recruitment_analytics(
    current_user=Depends(
        get_current_company_admin
    ),
    db: AsyncSession = Depends(get_db),
):

    service = OrganizationAnalyticsService(db)

    return await (
        service.get_job_wise_recruitment_analytics(
            current_user.company_id
        )
    )


# ============================================================
# GET HIRING RATE
# ============================================================

@router.get(
    "/recruitment/hiring-rate"
)
async def get_hiring_rate(
    current_user=Depends(
        get_current_company_admin
    ),
    db: AsyncSession = Depends(get_db),
):

    service = OrganizationAnalyticsService(db)

    return await (
        service.get_hiring_rate(
            current_user.company_id
        )
    )


# ============================================================
# GET AVERAGE TIME TO HIRE
# ============================================================

@router.get(
    "/recruitment/average-time-to-hire"
)
async def get_average_time_to_hire(
    current_user=Depends(
        get_current_company_admin
    ),
    db: AsyncSession = Depends(get_db),
):

    service = OrganizationAnalyticsService(db)

    return await (
        service.get_average_time_to_hire(
            current_user.company_id
        )
    )


# ============================================================
# GET COMPLETE RECRUITMENT DASHBOARD
# ============================================================

@router.get(
    "/recruitment/dashboard",
    response_model=RecruitmentDashboardResponse,
)
async def get_recruitment_dashboard(
    current_user=Depends(
        get_current_company_admin
    ),
    db: AsyncSession = Depends(get_db),
):

    service = OrganizationAnalyticsService(db)

    return await (
        service.get_recruitment_dashboard(
            current_user.company_id
        )
    )