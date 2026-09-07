from fastapi import (
    APIRouter,
    Depends,
    File as FastAPIFile,
    HTTPException,
    UploadFile,
    status,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db

from app.models.user import User
from app.models.user_profile import UserProfile

from app.schemas.file import FileUploadResponse

from app.services.file_service import FileService


router = APIRouter(
    prefix="/files",
    tags=["Files"],
)


# =========================================================
# NORMAL FILE UPLOAD
# =========================================================

@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Upload a normal file.

    Use this endpoint for:
    - Resume
    - Documents
    - Videos
    - Other supported files

    IMPORTANT:
    The returned `id` must be used as
    `resume_file_id` in /profiles/me.
    """

    # ---------------------------------------------------------
    # Validate filename
    # ---------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required.",
        )

    # ---------------------------------------------------------
    # File service
    # ---------------------------------------------------------

    service = FileService(session)

    try:

        created_file, public_url = (
            await service.upload_file(
                file=file,
                uploaded_by=current_user.id,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(exc),
        ) from exc

    # ---------------------------------------------------------
    # Commit file
    # ---------------------------------------------------------

    await session.commit()

    # ---------------------------------------------------------
    # Return file ID
    # ---------------------------------------------------------

    return FileUploadResponse(
        id=created_file.id,
        file_name=created_file.original_filename,
        file_url=public_url,
        content_type=created_file.content_type,
        size=created_file.size,
    )


# =========================================================
# PROFILE PHOTO UPLOAD
# =========================================================

@router.post(
    "/profile-photo",
    status_code=status.HTTP_201_CREATED,
)
async def upload_profile_photo(
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Upload a profile photo.

    This endpoint can be used before
    the profile is created.
    """

    # ---------------------------------------------------------
    # Validate filename
    # ---------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required.",
        )

    # ---------------------------------------------------------
    # Allowed image types
    # ---------------------------------------------------------

    allowed_content_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    if file.content_type not in allowed_content_types:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG, PNG, and WEBP images are allowed.",
        )

    # ---------------------------------------------------------
    # File service
    # ---------------------------------------------------------

    service = FileService(session)

    try:

        created_file, public_url = (
            await service.upload_file(
                file=file,
                uploaded_by=current_user.id,
                folder="profile-photos",
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(exc),
        ) from exc

    # ---------------------------------------------------------
    # Commit
    # ---------------------------------------------------------

    await session.commit()

    # ---------------------------------------------------------
    # Response
    # ---------------------------------------------------------

    return {
        "file_id": created_file.id,
        "public_url": public_url,
    }


# =========================================================
# UPDATE / REPLACE PROFILE PHOTO
# =========================================================

@router.put(
    "/profile-photo",
    response_model=FileUploadResponse,
    status_code=status.HTTP_200_OK,
)
async def update_profile_photo(
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Upload or replace the authenticated user's
    profile photo.
    """

    # ---------------------------------------------------------
    # Validate filename
    # ---------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required.",
        )

    # ---------------------------------------------------------
    # Allowed image types
    # ---------------------------------------------------------

    allowed_content_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    if file.content_type not in allowed_content_types:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only JPG, PNG, and WEBP images are allowed "
                "for profile photos."
            ),
        )

    # ---------------------------------------------------------
    # Get profile
    # ---------------------------------------------------------

    result = await session.execute(
        select(UserProfile)
        .where(
            UserProfile.user_id == current_user.id
        )
    )

    profile = result.scalar_one_or_none()

    if profile is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    # ---------------------------------------------------------
    # File service
    # ---------------------------------------------------------

    service = FileService(session)

    try:

        created_file, public_url = (
            await service.upload_file(
                file=file,
                uploaded_by=current_user.id,
                folder="profile-photos",
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(exc),
        ) from exc

    # ---------------------------------------------------------
    # Assign new photo
    # ---------------------------------------------------------

    profile.profile_photo_file_id = (
        created_file.id
    )

    # ---------------------------------------------------------
    # Commit
    # ---------------------------------------------------------

    await session.commit()

    await session.refresh(profile)

    # ---------------------------------------------------------
    # Response
    # ---------------------------------------------------------

    return FileUploadResponse(
        id=created_file.id,
        file_name=created_file.original_filename,
        file_url=public_url,
        content_type=created_file.content_type,
        size=created_file.size,
    )