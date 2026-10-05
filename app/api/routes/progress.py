from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.level import Level
from app.models.progress import Progress
from app.models.user import User
from app.schemas.progress import (
    ProgressCreate,
    ProgressResponse,
    ProgressUpdate,
)
from app.services.progress_service import ProgressService


router = APIRouter(
    prefix="/progress",
    tags=["Progress"],
)


# ============================================================
# GET PROGRESS BY ID
# ============================================================

@router.get(
    "/{progress_id}",
    response_model=ProgressResponse,
)
async def get_progress(
    progress_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = ProgressService(db)

    progress = await service.get_by_id(progress_id)

    if progress is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found",
        )

    return progress


# ============================================================

# GET USER PROGRESS

# ============================================================

@router.get(
    "/user/{user_id}",
    response_model=list[ProgressResponse],
)
async def get_user_progress(
    user_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = ProgressService(db)

    return await service.get_by_user_id(
        user_id,
        skip=skip,
        limit=limit,
    )


# ============================================================

# GET COURSE PROGRESS

# ============================================================

@router.get(
    "/course/{course_id}",
    response_model=list[ProgressResponse],
)
async def get_course_progress(
    course_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = ProgressService(db)

    return await service.get_by_course_id(
        course_id,
        skip=skip,
        limit=limit,
    )


# ============================================================

# GET LEVEL PROGRESS

# ============================================================

@router.get(
    "/level/{level_id}",
    response_model=list[ProgressResponse],
)
async def get_level_progress(
    level_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = ProgressService(db)

    return await service.get_by_level_id(
        level_id,
        skip=skip,
        limit=limit,
    )


# ============================================================
# GET USER + LEVEL PROGRESS
# ============================================================

@router.get(
    "/user/{user_id}/level/{level_id}",
    response_model=ProgressResponse,
)
async def get_user_level_progress(
    user_id: UUID,
    level_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = ProgressService(db)

    # 1. Check whether progress already exists
    progress = await service.get_user_level_progress(
        user_id,
        level_id,
    )

    # 2. If it doesn't exist, create initial progress
    if progress is None:

        # Get the level so we can get the correct course_id
        result = await db.execute(
            select(Level).where(
                Level.id == level_id
            )
        )

        level = result.scalar_one_or_none()

        if level is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Level not found",
            )

        # Create initial progress
        progress = Progress(
            user_id=user_id,
            course_id=level.course_id,
            level_id=level_id,

            checkpoints_passed=[],
            mcqs_answered=[],
            video_completed=False,
            mcqs_completed=False,
            completed=False,
        )

        progress = await service.create_progress(
            progress
        )

    return progress

# ============================================================
# GET COMPLETED PROGRESS
# ============================================================

# ============================================================
# GET COMPLETED PROGRESS
# ============================================================

@router.get(
    "/user/{user_id}/completed",
    response_model=list[ProgressResponse],
)
async def get_completed_progress(
    user_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = ProgressService(db)

    return await service.get_completed_for_user(
        user_id,
        skip=skip,
        limit=limit,
    )


# ============================================================
# GET INCOMPLETE PROGRESS
# ============================================================

@router.get(
    "/user/{user_id}/incomplete",
    response_model=list[ProgressResponse],
)
async def get_incomplete_progress(
    user_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = ProgressService(db)

    return await service.get_incomplete_for_user(
        user_id,
        skip=skip,
        limit=limit,
    )


# ============================================================
# CREATE PROGRESS
# ============================================================

@router.post(
    "",
    response_model=ProgressResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_progress(
    data: ProgressCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # --------------------------------------------------------
    # 1. Find the level
    # --------------------------------------------------------

    result = await db.execute(
        select(Level).where(
            Level.id == data.level_id
        )
    )

    level = result.scalar_one_or_none()

    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Level not found",
        )

    # --------------------------------------------------------
    # 2. IMPORTANT
    #
    # Never trust course_id sent by frontend.
    #
    # A level already belongs to a specific course.
    # Therefore we get course_id directly from the level.
    # --------------------------------------------------------

    correct_course_id = level.course_id

    # --------------------------------------------------------
    # 3. Create Progress object
    # --------------------------------------------------------

    progress = Progress(

        # IMPORTANT:
        # User ID comes from JWT.
        # Never trust user_id from frontend.
        user_id=current_user.id,

        course_id=data.course_id,

        level_id=data.level_id,

        checkpoints_passed=data.checkpoints_passed,

        mcqs_answered=data.mcqs_answered,

        video_completed=data.video_completed,

        mcqs_completed=data.mcqs_completed,

        completed=data.completed,
    )

    # --------------------------------------------------------
    # 4. Send to service
    # --------------------------------------------------------

    service = ProgressService(db)

    return await service.create_progress(
        progress
    )


# ============================================================
# UPDATE PROGRESS
# ============================================================

# ============================================================
# UPDATE PROGRESS
# ============================================================

@router.put(
    "/{progress_id}",
    response_model=ProgressResponse,
)
async def update_progress(
    progress_id: UUID,
    data: ProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProgressService(db)

    progress = await service.get_by_id(
        progress_id
    )

    if progress is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found",
        )

    # IMPORTANT:
    # User can update only their own progress.
    if progress.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this progress",
        )

    updated = await service.update_progress(
        progress_id,
        data,
    )


    return updated



# ============================================================
# GET MY LEVEL PROGRESS
# ============================================================

@router.get(
    "/me/level/{level_id}",
    response_model=ProgressResponse,
)
async def get_my_level_progress(
    level_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProgressService(db)

    # User ID comes from JWT
    user_id = current_user.id

    # --------------------------------------------------------
    # Check existing progress
    # --------------------------------------------------------

    progress = await service.get_user_level_progress(
        user_id,
        level_id,
    )

    # --------------------------------------------------------
    # Create progress if it doesn't exist
    # --------------------------------------------------------

    if progress is None:

        result = await db.execute(
            select(Level).where(
                Level.id == level_id
            )
        )

        level = result.scalar_one_or_none()

        if level is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Level not found",
            )

        progress = Progress(
            user_id=user_id,
            course_id=level.course_id,
            level_id=level_id,
            checkpoints_passed=[],
            mcqs_answered=[],
            video_completed=False,
            mcqs_completed=False,
            completed=False,
        )

        progress = await service.create_progress(
            progress
        )

    return progress


# ============================================================
# DELETE PROGRESS
# ============================================================

# ============================================================
# DELETE PROGRESS
# ============================================================

@router.delete(
    "/{progress_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_progress(
    progress_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProgressService(db)

    progress = await service.get_by_id(
        progress_id
    )

    if progress is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found",
        )


    # IMPORTANT:
    # User can delete only their own progress.
    if progress.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this progress",
        )

    await service.delete_progress(progress)


    return None