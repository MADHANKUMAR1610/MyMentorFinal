from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.mentor_application import MentorApplication
from app.models.user import User
from app.schemas.mentor_application import (
    MentorApplicationCreate,
    MentorApplicationResponse,
    MentorApplicationUpdate,
)
from app.services.mentor_application_service import (
    MentorApplicationService,
)


router = APIRouter(
    prefix="/mentor-applications",
    tags=["Mentor Applications"],
)


# ============================================================
# CREATE MENTOR APPLICATION
# ============================================================

@router.post(
    "",
    response_model=MentorApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_mentor_application(
    data: MentorApplicationCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Submit a mentor application.
    """

    service = MentorApplicationService(session)

    existing_application = await service.get_by_email(
        data.email
    )

    if existing_application is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A mentor application already exists for this email.",
        )

    application = MentorApplication(
        name=data.name,
        email=data.email,
        phone=data.phone,
        role=data.role,
        company=data.company,
        industry=data.industry,
        experience_years=data.experience_years,
        skills=data.skills,
        languages=data.languages,
        linkedin=data.linkedin,
        bio=data.bio,
        motivation=data.motivation,
        status="pending",
    )

    created_application = await service.create_application(
        application
    )

    return MentorApplicationResponse.model_validate(
        created_application
    )


# ============================================================
# GET MENTOR APPLICATION BY ID
# ============================================================

@router.get(
    "/{application_id}",
    response_model=MentorApplicationResponse,
)
async def get_mentor_application_by_id(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get a mentor application by UUID.
    """

    service = MentorApplicationService(session)

    application = await service.get_by_id(
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor application not found.",
        )

    return MentorApplicationResponse.model_validate(
        application
    )


# ============================================================
# GET APPLICATIONS
# ============================================================

@router.get(
    "",
    response_model=list[MentorApplicationResponse],
)
async def get_mentor_applications(
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
    Get mentor applications with optional filters.
    """

    service = MentorApplicationService(session)

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
        MentorApplicationResponse.model_validate(
            application
        )
        for application in applications
    ]


# ============================================================
# UPDATE MENTOR APPLICATION
# ============================================================

@router.put(
    "/{application_id}",
    response_model=MentorApplicationResponse,
)
async def update_mentor_application(
    application_id: UUID,
    data: MentorApplicationUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Update a mentor application.
    """

    service = MentorApplicationService(session)

    application = await service.get_by_id(
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor application not found.",
        )

    if data.phone is not None:
        application.phone = data.phone

    if data.role is not None:
        application.role = data.role

    if data.company is not None:
        application.company = data.company

    if data.industry is not None:
        application.industry = data.industry

    if data.experience_years is not None:
        application.experience_years = data.experience_years

    if data.skills is not None:
        application.skills = data.skills

    if data.languages is not None:
        application.languages = data.languages

    if data.linkedin is not None:
        application.linkedin = data.linkedin

    if data.bio is not None:
        application.bio = data.bio

    if data.motivation is not None:
        application.motivation = data.motivation

    if data.status is not None:
        application.status = data.status

    updated_application = await service.update_application(
        application
    )

    return MentorApplicationResponse.model_validate(
        updated_application
    )


# ============================================================
# DELETE MENTOR APPLICATION
# ============================================================

@router.delete(
    "/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_mentor_application(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Delete a mentor application.
    """

    service = MentorApplicationService(session)

    application = await service.get_by_id(
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor application not found.",
        )

    await service.delete_application(
        application
    )

    return None