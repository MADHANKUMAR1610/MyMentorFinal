from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.mentor import Mentor
from app.models.user import User
from app.schemas.mentor import (
    MentorCreate,
    MentorResponse,
    MentorUpdate,
)
from app.services.mentor_service import MentorService


router = APIRouter(
    prefix="/mentors",
    tags=["Mentors"],
)


# ============================================================
# GET MENTOR BY ID
# ============================================================

@router.get(
    "/{mentor_id}",
    response_model=MentorResponse,
)
async def get_mentor_by_id(
    mentor_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get a mentor by UUID.
    """

    service = MentorService(session)

    mentor = await service.get_by_id(mentor_id)

    if mentor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor not found.",
        )

    return MentorResponse.model_validate(mentor)


# ============================================================
# GET MENTORS
# ============================================================

@router.get(
    "",
    response_model=list[MentorResponse],
)
async def get_mentors(
    industry: str | None = Query(default=None),
    role: str | None = Query(default=None),
    mentor_status: str | None = Query(
        default=None,
        alias="status",
    ),
    verified: bool | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get mentors with optional filters.
    """

    service = MentorService(session)

    if industry is not None:
        mentors = await service.get_by_industry(
            industry,
            skip=skip,
            limit=limit,
        )

    elif role is not None:
        mentors = await service.get_by_role(
            role,
            skip=skip,
            limit=limit,
        )

    elif mentor_status is not None:
        mentors = await service.get_by_status(
            mentor_status,
            skip=skip,
            limit=limit,
        )

    elif verified is True:
        mentors = await service.get_verified(
            skip=skip,
            limit=limit,
        )

    else:
        mentors = await service.repository.get_all(
            skip=skip,
            limit=limit,
        )

    return [
        MentorResponse.model_validate(mentor)
        for mentor in mentors
    ]


# ============================================================
# CREATE MENTOR
# ============================================================

@router.post(
    "",
    response_model=MentorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_mentor(
    data: MentorCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Create a mentor.
    """

    service = MentorService(session)

    mentor = Mentor(
        name=data.name,
        role=data.role,
        company=data.company,
        industry=data.industry,
        image_url=data.image_url,
        experience_years=data.experience_years,
        languages=data.languages,
        skills=data.skills,
        rating=data.rating,
        price=data.price,
        availability=data.availability,
        status=data.status,
        verified=data.verified,
    )

    created_mentor = await service.create_mentor(
        mentor
    )

    return MentorResponse.model_validate(
        created_mentor
    )


# ============================================================
# UPDATE MENTOR
# ============================================================

@router.put(
    "/{mentor_id}",
    response_model=MentorResponse,
)
async def update_mentor(
    mentor_id: UUID,
    data: MentorUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Update a mentor.
    """

    service = MentorService(session)

    mentor = await service.get_by_id(
        mentor_id
    )

    if mentor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor not found.",
        )

    if data.name is not None:
        mentor.name = data.name

    if data.role is not None:
        mentor.role = data.role

    if data.company is not None:
        mentor.company = data.company

    if data.industry is not None:
        mentor.industry = data.industry

    if data.image_url is not None:
        mentor.image_url = data.image_url

    if data.experience_years is not None:
        mentor.experience_years = data.experience_years

    if data.languages is not None:
        mentor.languages = data.languages

    if data.skills is not None:
        mentor.skills = data.skills

    if data.rating is not None:
        mentor.rating = data.rating

    if data.price is not None:
        mentor.price = data.price

    if data.availability is not None:
        mentor.availability = data.availability

    if data.status is not None:
        mentor.status = data.status

    if data.verified is not None:
        mentor.verified = data.verified

    updated_mentor = await service.update_mentor(
        mentor
    )

    return MentorResponse.model_validate(
        updated_mentor
    )


# ============================================================
# DELETE MENTOR
# ============================================================

@router.delete(
    "/{mentor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_mentor(
    mentor_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Delete a mentor.
    """

    service = MentorService(session)

    mentor = await service.get_by_id(
        mentor_id
    )

    if mentor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor not found.",
        )

    await service.delete_mentor(mentor)

    return None