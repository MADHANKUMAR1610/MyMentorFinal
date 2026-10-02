from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.models.level import Level
from app.models.progress import Progress
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
# GET PROGRESS BY USER
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
# GET PROGRESS BY COURSE
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
# GET PROGRESS BY LEVEL
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

            checkpoints_passed=0,
            mcqs_answered=0,
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
        user_id=data.user_id,

        # IMPORTANT:
        # Use the course_id from the level
        course_id=correct_course_id,

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

@router.put(
    "/{progress_id}",
    response_model=ProgressResponse,
)
async def update_progress(
    progress_id: UUID,
    data: ProgressUpdate,
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

    update_data = data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(
            progress,
            field,
            value,
        )

    return await service.update_progress(
        progress
    )


# ============================================================
# DELETE PROGRESS
# ============================================================

@router.delete(
    "/{progress_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_progress(
    progress_id: UUID,
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

    await service.delete_progress(
        progress
    )

    return None