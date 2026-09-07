import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.api.dependencies import get_current_user
from app.database.database import get_db

from app.models.file import File
from app.models.user_profile import UserProfile

from app.schemas.user_profile import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
)

from app.services.user_profile_service import (
    UserProfileService,
)


router = APIRouter(
    prefix="/profiles",
    tags=["User Profiles"],
)


# =========================================================
# GET MY PROFILE
# =========================================================

@router.get(
    "/me",
    response_model=UserProfileResponse,
)
async def get_my_profile(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = UserProfileService(db)

    profile = await service.get_by_user_id(
        current_user.id
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    return UserProfileResponse.model_validate(
        service.build_profile_response(profile)
    )


# =========================================================
# CREATE MY PROFILE
# =========================================================

@router.post(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_my_profile(
    data: UserProfileCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = UserProfileService(db)

    # -----------------------------------------------------
    # CHECK EXISTING PROFILE
    # -----------------------------------------------------

    existing_profile = await service.get_by_user_id(
        current_user.id
    )

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User profile already exists",
        )

    # -----------------------------------------------------
    # VALIDATE RESUME FILE
    # -----------------------------------------------------

    if data.resume_file_id is not None:

        result = await db.execute(
            select(File).where(
                File.id == data.resume_file_id,
                File.uploaded_by == current_user.id,
                File.is_deleted.is_(False),
            )
        )

        resume_file = result.scalar_one_or_none()

        if resume_file is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid resume file.",
            )

    # -----------------------------------------------------
    # VALIDATE PROFILE PHOTO
    # -----------------------------------------------------

    if data.profile_photo_file_id is not None:

        result = await db.execute(
            select(File).where(
                File.id == data.profile_photo_file_id,
                File.uploaded_by == current_user.id,
                File.is_deleted.is_(False),
            )
        )

        profile_photo = result.scalar_one_or_none()

        if profile_photo is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid profile photo file.",
            )

    # -----------------------------------------------------
    # CREATE PROFILE
    # -----------------------------------------------------

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

        profile_photo_file_id=data.profile_photo_file_id,
        resume_file_id=data.resume_file_id,
    )

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    db.add(profile)

    await db.commit()

    # -----------------------------------------------------
    # RE-FETCH WITH FILE RELATIONSHIPS
    # -----------------------------------------------------

    result = await db.execute(
        select(UserProfile)
        .options(
            joinedload(
                UserProfile.profile_photo
            ),
            joinedload(
                UserProfile.resume_file
            ),
            joinedload(
                UserProfile.work_experiences
            ),
        )
        .where(
            UserProfile.user_id == current_user.id
        )
    )

    created_profile = (
        result
        .unique()
        .scalar_one_or_none()
    )

    if not created_profile:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile creation failed",
        )

    return UserProfileResponse.model_validate(
        service.build_profile_response(
            created_profile
        )
    )


# =========================================================
# UPDATE MY PROFILE
# =========================================================

@router.put(
    "/me",
    response_model=UserProfileResponse,
)
async def update_my_profile(
    data: UserProfileUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = UserProfileService(db)

    # -----------------------------------------------------
    # GET PROFILE
    # -----------------------------------------------------

    result = await db.execute(
        select(UserProfile)
        .where(
            UserProfile.user_id == current_user.id
        )
    )

    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    # -----------------------------------------------------
    # BASIC FIELDS
    # -----------------------------------------------------

    if data.dob is not None:
        profile.dob = data.dob

    if data.age is not None:
        profile.age = data.age

    if data.profile_category is not None:
        profile.profile_category = (
            data.profile_category
        )

    if data.education is not None:
        profile.education = data.education

    if data.class_year is not None:
        profile.class_year = data.class_year

    if data.institution is not None:
        profile.institution = data.institution

    if data.career_goal is not None:
        profile.career_goal = data.career_goal

    if data.career_interests is not None:
        profile.career_interests = (
            data.career_interests
        )

    # -----------------------------------------------------
    # PROFILE PHOTO
    # -----------------------------------------------------

    if data.profile_photo_file_id is not None:

        result = await db.execute(
            select(File).where(
                File.id == data.profile_photo_file_id,
                File.uploaded_by == current_user.id,
                File.is_deleted.is_(False),
            )
        )

        profile_photo = result.scalar_one_or_none()

        if profile_photo is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid profile photo file.",
            )

        profile.profile_photo_file_id = (
            data.profile_photo_file_id
        )

    # -----------------------------------------------------
    # RESUME
    # -----------------------------------------------------

    if data.resume_file_id is not None:

        result = await db.execute(
            select(File).where(
                File.id == data.resume_file_id,
                File.uploaded_by == current_user.id,
                File.is_deleted.is_(False),
            )
        )

        resume_file = result.scalar_one_or_none()

        if resume_file is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid resume file.",
            )

        # THIS IS THE IMPORTANT PART
        profile.resume_file_id = (
            data.resume_file_id
        )

    # -----------------------------------------------------
    # COMMIT DIRECTLY
    # -----------------------------------------------------

    await db.commit()

    # -----------------------------------------------------
    # RE-FETCH PROFILE WITH RESUME
    # -----------------------------------------------------

    result = await db.execute(
        select(UserProfile)
        .options(
            joinedload(
                UserProfile.profile_photo
            ),
            joinedload(
                UserProfile.resume_file
            ),
            joinedload(
                UserProfile.work_experiences
            ),
        )
        .where(
            UserProfile.user_id == current_user.id
        )
    )

    updated_profile = (
        result
        .unique()
        .scalar_one_or_none()
    )

    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed",
        )

    return UserProfileResponse.model_validate(
        service.build_profile_response(
            updated_profile
        )
    )


# =========================================================
# DELETE MY PROFILE
# =========================================================

@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_my_profile(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = UserProfileService(db)

    profile = await service.get_by_user_id(
        current_user.id
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    await service.delete_profile(profile)

    return None


# =========================================================
# GET PROFILE BY ID
# =========================================================

@router.get(
    "/{profile_id}",
    response_model=UserProfileResponse,
)
async def get_profile_by_id(
    profile_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = UserProfileService(db)

    profile = await service.get_by_id(
        profile_id
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    return UserProfileResponse.model_validate(
        service.build_profile_response(profile)
    )