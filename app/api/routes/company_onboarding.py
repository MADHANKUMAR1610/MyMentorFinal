from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.schemas.company_onboarding import (
    CompanyOnboardingCreate,
    CompanyOnboardingResponse,
)
from app.services.company_onboarding_service import (
    CompanyOnboardingService,
)


router = APIRouter(
    prefix="/companies",
    tags=["Company Onboarding"],
)


# ============================================================
# COMPANY ONBOARDING
# ============================================================

@router.post(
    "/onboarding",
    response_model=CompanyOnboardingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def company_onboarding(
    data: CompanyOnboardingCreate,
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CompanyOnboardingService(
        session
    )

    try:

        company, admin_user = (
            await service.create_company(
                data
            )
        )

    except ValueError as exc:

        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    except Exception as exc:

        await session.rollback()

        print(
            "Company onboarding error:",
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Company onboarding failed.",
        )

    return CompanyOnboardingResponse(
        company_id=str(
            company.id
        ),

        admin_user_id=str(
            admin_user.id
        ),

        company_name=company.name,

        contact_person_name=(
            company.contact_person_name
        ),

        contact_email=(
            company.contact_email
        ),

        admin_official_email=(
            admin_user.email
        ),

        role=admin_user.role,

        message=(
            "Company onboarding completed successfully."
        ),
    )