from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db

from app.models.file import File
from app.models.user import User
from app.models.user_profile import UserProfile

from app.schemas.user_profile import (
    UserProfileCreate,
    UserProfileResponse,
    UserProfileUpdate,
    ProfileSummaryResponse,
    ScoreBreakdownResponse,
)
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.services.user_profile_service import UserProfileService


router = APIRouter(
    prefix="/profiles",
    tags=["User Profiles"],
)


# ============================================================
# GET MY PROFILE SUMMARY
# ============================================================

@router.get(
    "/me/summary",
    response_model=ProfileSummaryResponse,
)
async def get_my_profile_summary(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get the profile summary displayed at the top
    of the MyMentor profile page.
    """

    service = UserProfileService(session)

    profile = await service.get_by_user_id(
        current_user.id
    )

    return await service.get_profile_summary(
        user_id=current_user.id,
    )


# ============================================================
# GET MY SCORE BREAKDOWN
# ============================================================

@router.get(
    "/me/score-breakdown",
    response_model=ScoreBreakdownResponse,
)
async def get_my_score_breakdown(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get the score breakdown displayed on
    the MyMentor profile page.
    """

    service = UserProfileService(session)

    profile = await service.get_by_user_id(
        current_user.id
    )

    return await service.get_score_breakdown(
        user_id=current_user.id,
    )


# ============================================================
# GET MY PROFILE
# ============================================================

@router.get(
    "/me",
    response_model=UserProfileResponse,
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get the currently authenticated user's profile
    including profile photo URL.
    """

    service = UserProfileService(session)

    # ---------------------------------------------------------
    # Get user profile
    # ---------------------------------------------------------

    profile = await service.get_by_user_id(
        current_user.id
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    # ---------------------------------------------------------
    # Get profile photo URL
    # ---------------------------------------------------------

    profile_photo_url = None

    if profile.profile_photo_file_id is not None:

        result = await session.execute(
            select(File).where(
                File.id == profile.profile_photo_file_id,
                File.is_deleted.is_(False),
            )
        )

        profile_photo = result.scalar_one_or_none()

        if profile_photo is not None:
            profile_photo_url = profile_photo.public_url

    resume_url = None
    resume_file_name = None

    if (
        profile.resume_file
        and not profile.resume_file.is_deleted
    ):
        resume_url = profile.resume_file.public_url
        resume_file_name = profile.resume_file.original_filename
    # ---------------------------------------------------------
    # Return profile
    # ---------------------------------------------------------

    return UserProfileResponse(
        id=profile.id,
        user_id=profile.user_id,

        dob=profile.dob,
        age=profile.age,
        profile_category=profile.profile_category,
        education=profile.education,
        class_year=profile.class_year,
        institution=profile.institution,
        career_goal=profile.career_goal,
        career_interests=profile.career_interests,

        profile_photo_file_id=profile.profile_photo_file_id,
        resume_file_name=resume_file_name,
        profile_photo_url=profile_photo_url,
        resume_file_id=profile.resume_file_id,
        resume_url=resume_url,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


# ============================================================
# CREATE MY PROFILE
# ============================================================

@router.post(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_my_profile(
    data: UserProfileCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Create a profile for the currently authenticated user.
    """

    service = UserProfileService(session)

    # ---------------------------------------------------------
    # Check if profile already exists
    # ---------------------------------------------------------

    existing_profile = await service.get_by_user_id(
        current_user.id
    )

    if existing_profile is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User profile already exists.",
        )

    # ---------------------------------------------------------
    # Validate profile photo
    # ---------------------------------------------------------

    profile_photo_file = None

    if data.profile_photo_file_id is not None:

        result = await session.execute(
            select(File).where(
                File.id == data.profile_photo_file_id,
                File.uploaded_by == current_user.id,
                File.is_deleted.is_(False),
            )
        )

        profile_photo_file = result.scalar_one_or_none()

        if profile_photo_file is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile photo file not found.",
            )

        allowed_content_types = {
            "image/jpeg",
            "image/png",
            "image/webp",
        }

        if profile_photo_file.content_type not in allowed_content_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Only JPG, PNG, and WEBP images "
                    "can be used as a profile photo."
                ),
            )

    # ---------------------------------------------------------
    # Validate resume
    # ---------------------------------------------------------

    resume_file = None

    if data.resume_file_id is not None:

        result = await session.execute(
            select(File).where(
                File.id == data.resume_file_id,
                File.uploaded_by == current_user.id,
                File.is_deleted.is_(False),
            )
        )

        resume_file = result.scalar_one_or_none()

        if resume_file is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume file not found.",
            )

        allowed_resume_types = {
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }

        if resume_file.content_type not in allowed_resume_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Only PDF, DOC, and DOCX files "
                    "can be used as a resume."
                ),
            )

    # ---------------------------------------------------------
    # Create profile
    # ---------------------------------------------------------

    profile = UserProfile(
        user_id=current_user.id,
        dob=data.dob,
        age=data.age,
        profile_category=data.profile_category,
        education=data.education,
        class_year=data.class_year,
        institution=data.institution,
        career_goal=data.career_goal,
        career_interests=data.career_interests,

        # IMPORTANT
        profile_photo_file_id=(
            profile_photo_file.id
            if profile_photo_file is not None
            else None
        ),

        # IMPORTANT
        resume_file_id=(
            resume_file.id
            if resume_file is not None
            else None
        ),
    )

    created_profile = await service.create_profile(
        profile
    )

    # ---------------------------------------------------------
    # Reload profile with related files
    # ---------------------------------------------------------

    result = await session.execute(
        select(UserProfile)
        .options(
            joinedload(UserProfile.profile_photo),
            joinedload(UserProfile.resume_file),
        )
        .where(UserProfile.id == created_profile.id)
    )

    created_profile = result.unique().scalar_one()

    # ---------------------------------------------------------
    # Return response
    # ---------------------------------------------------------

    return UserProfileResponse.model_validate(
        service.build_profile_response(created_profile)
    )
# ============================================================
# UPDATE MY PROFILE
# ============================================================

@router.put(
    "/me",
    response_model=UserProfileResponse,
)
async def update_my_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Update the currently authenticated user's profile.

    This endpoint also supports updating the profile photo.
    """

    service = UserProfileService(session)

    profile = await service.get_by_user_id(
        current_user.id
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    # ========================================================
    # NORMAL PROFILE FIELDS
    # ========================================================

    if data.dob is not None:
        profile.dob = data.dob

    if data.age is not None:
        profile.age = data.age

    if data.profile_category is not None:
        profile.profile_category = data.profile_category

    if data.education is not None:
        profile.education = data.education

    if data.class_year is not None:
        profile.class_year = data.class_year

    if data.institution is not None:
        profile.institution = data.institution

    if data.career_goal is not None:
        profile.career_goal = data.career_goal

    if data.career_interests is not None:
        profile.career_interests = data.career_interests

    # ========================================================
    # PROFILE PHOTO
    # ========================================================

    if data.profile_photo_file_id is not None:

        result = await session.execute(
            select(File).where(
                File.id == data.profile_photo_file_id,
                File.uploaded_by == current_user.id,
                File.is_deleted.is_(False),
            )
        )

        file = result.scalar_one_or_none()

        if file is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile photo file not found.",
            )

        # ----------------------------------------------------
        # Only images
        # ----------------------------------------------------

        allowed_content_types = {
            "image/jpeg",
            "image/png",
            "image/webp",
        }

        if file.content_type not in allowed_content_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Only JPG, PNG, and WEBP images "
                    "can be used as a profile photo."
                ),
            )

        # ----------------------------------------------------
        # Save profile photo file ID
        # ----------------------------------------------------

        profile.profile_photo_file_id = file.id
    # ========================================================
    # RESUME
    # ========================================================

    if data.resume_file_id is not None:

        result = await session.execute(
            select(File).where(
                File.id == data.resume_file_id,
                File.uploaded_by == current_user.id,
                File.is_deleted.is_(False),
            )
        )

        resume_file = result.scalar_one_or_none()

        if resume_file is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume file not found.",
            )

        # ----------------------------------------------------
        # Validate resume file type
        # ----------------------------------------------------

        allowed_resume_types = {
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }

        if resume_file.content_type not in allowed_resume_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF, DOC, and DOCX files can be used as a resume.",
            )

        # ----------------------------------------------------
        # Save resume file ID
        # ----------------------------------------------------

        profile.resume_file_id = resume_file.id
    # ========================================================
    # SAVE PROFILE
    # ========================================================

    updated_profile = await service.update_profile(profile)

    result = await session.execute(
        select(UserProfile)
        .options(
            joinedload(UserProfile.profile_photo),
            joinedload(UserProfile.resume_file),
        )
        .where(UserProfile.id == updated_profile.id)
    )

    updated_profile = result.unique().scalar_one()

    return UserProfileResponse.model_validate(
        service.build_profile_response(updated_profile)
    )

# ============================================================
# DELETE MY PROFILE
# ============================================================

@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_my_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Delete the currently authenticated user's profile.
    """

    service = UserProfileService(session)

    profile = await service.get_by_user_id(
        current_user.id
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    await service.delete_profile(profile)

    return None


# ============================================================
# GET PROFILE BY ID
# ============================================================

@router.get(
    "/{profile_id}",
    response_model=UserProfileResponse,
)
async def get_profile_by_id(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get a user profile by profile UUID.
    """

    service = UserProfileService(session)

    result = await session.execute(
        select(UserProfile)
        .options(
            joinedload(UserProfile.profile_photo),
            joinedload(UserProfile.resume_file),
        )
        .where(UserProfile.id == profile_id)
    )

    profile = result.unique().scalar_one_or_none()

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    return UserProfileResponse.model_validate(
        service.build_profile_response(profile)
    )