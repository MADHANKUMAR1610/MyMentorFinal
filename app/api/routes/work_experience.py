from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.work_experience import WorkExperience

from app.schemas.work_experience import (
    WorkExperienceCreate,
    WorkExperienceUpdate,
    WorkExperienceResponse,
)


router = APIRouter(
    prefix="/work-experiences",
    tags=["Work Experiences"],
)


# ============================================================
# GET MY WORK EXPERIENCES
# ============================================================

@router.get(
    "/me",
    response_model=list[WorkExperienceResponse],
)
async def get_my_work_experiences(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get all work experiences of the currently
    authenticated user.
    """

    result = await session.execute(
        select(UserProfile).where(
            UserProfile.user_id == current_user.id
        )
    )

    profile = result.scalar_one_or_none()

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    result = await session.execute(
        select(WorkExperience)
        .where(
            WorkExperience.user_profile_id == profile.id
        )
        .order_by(
            WorkExperience.start_date.desc()
        )
    )

    experiences = result.scalars().all()

    return experiences


# ============================================================
# CREATE WORK EXPERIENCE
# ============================================================

@router.post(
    "/me",
    response_model=WorkExperienceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_my_work_experience(
    data: WorkExperienceCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Add a new work experience for the currently
    authenticated user.
    """

    # --------------------------------------------------------
    # Get current user's profile
    # --------------------------------------------------------

    result = await session.execute(
        select(UserProfile).where(
            UserProfile.user_id == current_user.id
        )
    )

    profile = result.scalar_one_or_none()

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    # --------------------------------------------------------
    # Validate dates
    # --------------------------------------------------------

    if (
        data.start_date is not None
        and data.end_date is not None
        and data.end_date < data.start_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date cannot be before start date.",
        )

    if data.currently_working:
        data_end_date = None
    else:
        data_end_date = data.end_date

    # --------------------------------------------------------
    # Create experience
    # --------------------------------------------------------

    experience = WorkExperience(
        user_profile_id=profile.id,
        company_name=data.company_name,
        job_title=data.job_title,
        employment_type=data.employment_type,
        location=data.location,
        start_date=data.start_date,
        end_date=data_end_date,
        currently_working=data.currently_working,
        description=data.description,
        skills=data.skills,
    )

    session.add(experience)

    await session.commit()
    await session.refresh(experience)

    return experience


# ============================================================
# UPDATE WORK EXPERIENCE
# ============================================================

@router.put(
    "/{experience_id}",
    response_model=WorkExperienceResponse,
)
async def update_work_experience(
    experience_id: UUID,
    data: WorkExperienceUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Update one work experience belonging to the
    currently authenticated user.
    """

    # --------------------------------------------------------
    # Get user profile
    # --------------------------------------------------------

    result = await session.execute(
        select(UserProfile).where(
            UserProfile.user_id == current_user.id
        )
    )

    profile = result.scalar_one_or_none()

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    # --------------------------------------------------------
    # Get experience
    # --------------------------------------------------------

    result = await session.execute(
        select(WorkExperience).where(
            WorkExperience.id == experience_id,
            WorkExperience.user_profile_id == profile.id,
        )
    )

    experience = result.scalar_one_or_none()

    if experience is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work experience not found.",
        )

    # --------------------------------------------------------
    # Update only provided fields
    # --------------------------------------------------------

    if data.company_name is not None:
        experience.company_name = data.company_name

    if data.job_title is not None:
        experience.job_title = data.job_title

    if data.employment_type is not None:
        experience.employment_type = data.employment_type

    if data.location is not None:
        experience.location = data.location

    if data.start_date is not None:
        experience.start_date = data.start_date

    if data.currently_working is not None:
        experience.currently_working = data.currently_working

    if data.description is not None:
        experience.description = data.description

    if data.skills is not None:
        experience.skills = data.skills

    # --------------------------------------------------------
    # End date handling
    # --------------------------------------------------------

    if experience.currently_working:
        experience.end_date = None
    elif data.end_date is not None:
        experience.end_date = data.end_date

    # --------------------------------------------------------
    # Validate dates
    # --------------------------------------------------------

    if (
        experience.start_date is not None
        and experience.end_date is not None
        and experience.end_date < experience.start_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date cannot be before start date.",
        )

    await session.commit()
    await session.refresh(experience)

    return experience


# ============================================================
# DELETE WORK EXPERIENCE
# ============================================================

@router.delete(
    "/{experience_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_work_experience(
    experience_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Delete one work experience belonging to the
    currently authenticated user.
    """

    # --------------------------------------------------------
    # Get user profile
    # --------------------------------------------------------

    result = await session.execute(
        select(UserProfile).where(
            UserProfile.user_id == current_user.id
        )
    )

    profile = result.scalar_one_or_none()

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    # --------------------------------------------------------
    # Get experience
    # --------------------------------------------------------

    result = await session.execute(
        select(WorkExperience).where(
            WorkExperience.id == experience_id,
            WorkExperience.user_profile_id == profile.id,
        )
    )

    experience = result.scalar_one_or_none()

    if experience is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work experience not found.",
        )

    await session.delete(experience)

    await session.commit()

    return None