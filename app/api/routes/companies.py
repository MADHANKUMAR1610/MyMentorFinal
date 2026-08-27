from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_current_user,
)

from app.database.database import get_db

from app.models.company import Company
from app.models.user import User

from app.schemas.company import (
    CompanyCreate,
    CompanyOnboardingCreate,
    CompanyResponse,
    CompanyUpdate,
)

from app.services.company_service import (
    CompanyService,
)


router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


# ============================================================
# COMPANY ONBOARDING
# ============================================================

@router.post(
    "/onboard",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def onboard_company(
    data: CompanyOnboardingCreate,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CompanyService(
        session
    )

    try:

        company = (
            await service.onboard_company(
                company_data=data,
                current_user=current_user,
            )
        )

    except ValueError as exc:

        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception:

        await session.rollback()

        raise

    return CompanyResponse.model_validate(
        company
    )


# ============================================================
# CREATE COMPANY
# ============================================================

@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_company(
    data: CompanyCreate,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CompanyService(
        session
    )

    # --------------------------------------------------------
    # CHECK EXISTING COMPANY
    # --------------------------------------------------------

    existing_company = (
        await service.get_by_name(
            data.name
        )
    )

    if existing_company is not None:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A company with this name "
                "already exists."
            ),
        )

    # --------------------------------------------------------
    # CREATE COMPANY
    # --------------------------------------------------------

    company = Company(

        # ====================================================
        # COMPANY PROFILE
        # ====================================================

        name=data.name,

        industry=data.industry,

        logo=data.logo,

        website=data.website,

        location=data.location,

        size=data.size,

        open_roles=data.open_roles,

        about=data.about,

        # ====================================================
        # CONTACT PERSON
        # ====================================================

        contact_person_name=(
            data.contact_person_name
        ),

        contact_email=(
            data.contact_email
        ),

        contact_phone=(
            data.contact_phone
        ),

        contact_role=(
            data.contact_role
        ),

        # ====================================================
        # STATUS
        # ====================================================

        status=data.status,

        verified=data.verified,
    )

    # --------------------------------------------------------
    # SAVE COMPANY
    # --------------------------------------------------------

    created_company = (
        await service.create_company(
            company
        )
    )

    return CompanyResponse.model_validate(
        created_company
    )


# ============================================================
# GET COMPANIES
# ============================================================

@router.get(
    "",
    response_model=list[CompanyResponse],
)
async def get_companies(

    industry: str | None = Query(
        default=None
    ),

    company_status: str | None = Query(
        default=None,
        alias="status",
    ),

    location: str | None = Query(
        default=None
    ),

    verified: bool | None = Query(
        default=None
    ),

    skip: int = Query(
        default=0,
        ge=0,
    ),

    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),

    current_user: User = Depends(
        get_current_user
    ),

    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CompanyService(
        session
    )

    # --------------------------------------------------------
    # FILTER BY INDUSTRY
    # --------------------------------------------------------

    if industry is not None:

        companies = (
            await service.get_by_industry(
                industry,
                skip=skip,
                limit=limit,
            )
        )

    # --------------------------------------------------------
    # FILTER BY STATUS
    # --------------------------------------------------------

    elif company_status is not None:

        companies = (
            await service.get_by_status(
                company_status,
                skip=skip,
                limit=limit,
            )
        )

    # --------------------------------------------------------
    # FILTER BY LOCATION
    # --------------------------------------------------------

    elif location is not None:

        companies = (
            await service.get_by_location(
                location,
                skip=skip,
                limit=limit,
            )
        )

    # --------------------------------------------------------
    # FILTER VERIFIED
    # --------------------------------------------------------

    elif verified is True:

        companies = (
            await service.get_verified(
                skip=skip,
                limit=limit,
            )
        )

    # --------------------------------------------------------
    # GET ALL
    # --------------------------------------------------------

    else:

        companies = (
            await service.repository.get_all(
                skip=skip,
                limit=limit,
            )
        )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return [
        CompanyResponse.model_validate(
            company
        )
        for company in companies
    ]


# ============================================================
# GET COMPANY BY ID
# ============================================================

@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
)
async def get_company_by_id(

    company_id: UUID,

    current_user: User = Depends(
        get_current_user
    ),

    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CompanyService(
        session
    )

    company = await service.get_by_id(
        company_id
    )

    if company is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )

    return CompanyResponse.model_validate(
        company
    )


# ============================================================
# UPDATE COMPANY
# ============================================================

@router.put(
    "/{company_id}",
    response_model=CompanyResponse,
)
async def update_company(

    company_id: UUID,

    data: CompanyUpdate,

    current_user: User = Depends(
        get_current_user
    ),

    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CompanyService(
        session
    )

    # --------------------------------------------------------
    # FIND COMPANY
    # --------------------------------------------------------

    company = await service.get_by_id(
        company_id
    )

    if company is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )

    # ========================================================
    # COMPANY PROFILE
    # ========================================================

    if data.name is not None:

        existing_company = (
            await service.get_by_name(
                data.name
            )
        )

        if (
            existing_company is not None
            and existing_company.id != company.id
        ):

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A company with this name "
                    "already exists."
                ),
            )

        company.name = data.name

    if data.industry is not None:

        company.industry = (
            data.industry
        )

    if data.logo is not None:

        company.logo = (
            data.logo
        )

    if data.website is not None:

        company.website = (
            data.website
        )

    if data.location is not None:

        company.location = (
            data.location
        )

    if data.size is not None:

        company.size = (
            data.size
        )

    if data.open_roles is not None:

        company.open_roles = (
            data.open_roles
        )

    if data.about is not None:

        company.about = (
            data.about
        )

    # ========================================================
    # CONTACT PERSON
    # ========================================================

    if data.contact_person_name is not None:

        company.contact_person_name = (
            data.contact_person_name
        )

    if data.contact_email is not None:

        company.contact_email = (
            data.contact_email
        )

    if data.contact_phone is not None:

        company.contact_phone = (
            data.contact_phone
        )

    if data.contact_role is not None:

        company.contact_role = (
            data.contact_role
        )

    # ========================================================
    # STATUS
    # ========================================================

    if data.status is not None:

        company.status = (
            data.status
        )

    if data.verified is not None:

        company.verified = (
            data.verified
        )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    updated_company = (
        await service.update_company(
            company
        )
    )

    return CompanyResponse.model_validate(
        updated_company
    )


# ============================================================
# DELETE COMPANY
# ============================================================

@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_company(

    company_id: UUID,

    current_user: User = Depends(
        get_current_user
    ),

    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CompanyService(
        session
    )

    company = await service.get_by_id(
        company_id
    )

    if company is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )

    await service.delete_company(
        company
    )

    return None