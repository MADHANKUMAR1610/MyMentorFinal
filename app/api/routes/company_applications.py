from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.company_application import CompanyApplication
from app.models.user import User
from app.schemas.company_application import (
    CompanyApplicationCreate,
    CompanyApplicationResponse,
    CompanyApplicationUpdate,
)
from app.services.company_application_service import (
    CompanyApplicationService,
)


router = APIRouter(
    prefix="/company-applications",
    tags=["Company Applications"],
)


# ============================================================
# CREATE COMPANY APPLICATION
# ============================================================

@router.post(
    "",
    response_model=CompanyApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_company_application(
    data: CompanyApplicationCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Submit a company application.
    """

    service = CompanyApplicationService(session)

    existing_application = await service.get_by_email(
        data.email
    )

    if existing_application is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A company application already exists for this email.",
        )

    application = CompanyApplication(
        company_name=data.company_name,
        website=data.website,
        industry=data.industry,
        contact_name=data.contact_name,
        email=data.email,
        size=data.size,
        location=data.location,
        about=data.about,
        hiring_needs=data.hiring_needs,
        submitted_by=current_user.id,
        status="pending",
    )

    created_application = await service.create_application(
        application
    )

    return CompanyApplicationResponse.model_validate(
        created_application
    )


# ============================================================
# GET MY APPLICATIONS
# ============================================================

@router.get(
    "/me",
    response_model=list[CompanyApplicationResponse],
)
async def get_my_company_applications(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get company applications submitted by the current user.
    """

    service = CompanyApplicationService(session)

    applications = await service.get_by_submitted_user(
        current_user.id,
        skip=skip,
        limit=limit,
    )

    return [
        CompanyApplicationResponse.model_validate(
            application
        )
        for application in applications
    ]


# ============================================================
# GET COMPANY APPLICATIONS
# ============================================================

@router.get(
    "",
    response_model=list[CompanyApplicationResponse],
)
async def get_company_applications(
    application_status: str | None = Query(
        default=None,
        alias="status",
    ),
    industry: str | None = Query(default=None),
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get company applications with optional filters.
    """

    service = CompanyApplicationService(session)

    if application_status is not None:
        applications = await service.get_by_status(
            application_status,
            skip=skip,
            limit=limit,
        )

    elif industry is not None:
        applications = await service.get_by_industry(
            industry,
            skip=skip,
            limit=limit,
        )

    else:
        applications = await service.repository.get_all(
            skip=skip,
            limit=limit,
        )

    return [
        CompanyApplicationResponse.model_validate(
            application
        )
        for application in applications
    ]


# ============================================================
# GET APPLICATION BY ID
# ============================================================

@router.get(
    "/{application_id}",
    response_model=CompanyApplicationResponse,
)
async def get_company_application_by_id(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get a company application by UUID.
    """

    service = CompanyApplicationService(session)

    application = await service.get_by_id(
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company application not found.",
        )

    if application.submitted_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this application.",
        )

    return CompanyApplicationResponse.model_validate(
        application
    )


# ============================================================
# UPDATE APPLICATION
# ============================================================

@router.put(
    "/{application_id}",
    response_model=CompanyApplicationResponse,
)
async def update_company_application(
    application_id: UUID,
    data: CompanyApplicationUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Update a company application belonging to the current user.
    """

    service = CompanyApplicationService(session)

    application = await service.get_by_id(
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company application not found.",
        )

    if application.submitted_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this application.",
        )

    if data.company_name is not None:
        application.company_name = data.company_name

    if data.website is not None:
        application.website = data.website

    if data.industry is not None:
        application.industry = data.industry

    if data.contact_name is not None:
        application.contact_name = data.contact_name

    if data.email is not None:
        existing_application = await service.get_by_email(
            data.email
        )

        if (
            existing_application is not None
            and existing_application.id != application.id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A company application already exists for this email.",
            )

        application.email = data.email

    if data.size is not None:
        application.size = data.size

    if data.location is not None:
        application.location = data.location

    if data.about is not None:
        application.about = data.about

    if data.hiring_needs is not None:
        application.hiring_needs = data.hiring_needs

    # Status should not normally be changed by the applicant.
    # We leave it unchanged here.
    updated_application = await service.update_application(
        application
    )

    return CompanyApplicationResponse.model_validate(
        updated_application
    )


# ============================================================
# DELETE APPLICATION
# ============================================================

@router.delete(
    "/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_company_application(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Delete a company application belonging to the current user.
    """

    service = CompanyApplicationService(session)

    application = await service.get_by_id(
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company application not found.",
        )

    if application.submitted_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this application.",
        )

    await service.delete_application(
        application
    )

    return None