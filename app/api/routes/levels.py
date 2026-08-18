from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.course import Course
from app.models.level import Level
from app.models.user import User
from app.schemas.level import (
    LevelCreate,
    LevelResponse,
    LevelUpdate,
)
from app.services.level_service import LevelService


router = APIRouter(
    prefix="/levels",
    tags=["Levels"],
)


# ============================================================
# CREATE LEVEL
# ============================================================

@router.post(
    "",
    response_model=LevelResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_level(
    data: LevelCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Create a level for a course.
    """

    course = await session.get(
        Course,
        data.course_id,
    )

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found.",
        )

    service = LevelService(session)

    existing_level = (
        await service.get_by_course_and_level_number(
            data.course_id,
            data.level_number,
        )
    )

    if existing_level is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This level number already exists for this course.",
        )

    level = Level(
        course_id=data.course_id,
        stage=data.stage,
        stage_order=data.stage_order,
        level_number=data.level_number,
        global_order=data.global_order,
        title=data.title,
        description=data.description,
        objectives=data.objectives,
        xp=data.xp,
        pass_percentage=data.pass_percentage,
        duration=data.duration,
        video=data.video,
        theory=data.theory,
    )

    created_level = await service.create_level(level)

    return LevelResponse.model_validate(created_level)


# ============================================================
# GET LEVELS
# ============================================================

@router.get(
    "",
    response_model=list[LevelResponse],
)
async def get_levels(
    course_id: UUID | None = Query(default=None),
    stage: str | None = Query(default=None),
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
    Get levels using optional filters.
    """

    service = LevelService(session)

    if course_id is not None:
        levels = await service.get_by_course_id(
            course_id,
            skip=skip,
            limit=limit,
        )

    elif stage is not None:
        levels = await service.get_by_stage(
            stage,
            skip=skip,
            limit=limit,
        )

    else:
        levels = await service.repository.get_all(
            skip=skip,
            limit=limit,
        )

    return [
        LevelResponse.model_validate(level)
        for level in levels
    ]


# ============================================================
# GET LEVEL BY GLOBAL ORDER
# ============================================================

@router.get(
    "/global/{global_order}",
    response_model=LevelResponse,
)
async def get_level_by_global_order(
    global_order: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get a level by its global order.
    """

    service = LevelService(session)

    level = await service.get_by_global_order(
        global_order
    )

    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Level not found.",
        )

    return LevelResponse.model_validate(level)


# ============================================================
# GET LEVEL BY COURSE + LEVEL NUMBER
# ============================================================

@router.get(
    "/course/{course_id}/number/{level_number}",
    response_model=LevelResponse,
)
async def get_level_by_course_and_number(
    course_id: UUID,
    level_number: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get a specific level inside a course.
    """

    service = LevelService(session)

    level = await service.get_by_course_and_level_number(
        course_id,
        level_number,
    )

    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Level not found.",
        )

    return LevelResponse.model_validate(level)


# ============================================================
# GET LEVEL BY ID
# ============================================================

@router.get(
    "/{level_id}",
    response_model=LevelResponse,
)
async def get_level_by_id(
    level_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get a level by UUID.
    """

    service = LevelService(session)

    level = await service.get_by_id(level_id)

    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Level not found.",
        )

    return LevelResponse.model_validate(level)


# ============================================================
# UPDATE LEVEL
# ============================================================

@router.put(
    "/{level_id}",
    response_model=LevelResponse,
)
async def update_level(
    level_id: UUID,
    data: LevelUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Update a level.
    """

    service = LevelService(session)

    level = await service.get_by_id(level_id)

    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Level not found.",
        )

    if data.stage is not None:
        level.stage = data.stage

    if data.stage_order is not None:
        level.stage_order = data.stage_order

    if data.level_number is not None:
        existing_level = (
            await service.get_by_course_and_level_number(
                level.course_id,
                data.level_number,
            )
        )

        if (
            existing_level is not None
            and existing_level.id != level.id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This level number already exists for this course.",
            )

        level.level_number = data.level_number

    if data.global_order is not None:
        level.global_order = data.global_order

    if data.title is not None:
        level.title = data.title

    if data.description is not None:
        level.description = data.description

    if data.objectives is not None:
        level.objectives = data.objectives

    if data.xp is not None:
        level.xp = data.xp

    if data.pass_percentage is not None:
        level.pass_percentage = data.pass_percentage

    if data.duration is not None:
        level.duration = data.duration

    if data.video is not None:
        level.video = data.video

    if data.theory is not None:
        level.theory = data.theory

    updated_level = await service.update_level(level)

    return LevelResponse.model_validate(updated_level)


# ============================================================
# DELETE LEVEL
# ============================================================

@router.delete(
    "/{level_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_level(
    level_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Delete a level.
    """

    service = LevelService(session)

    level = await service.get_by_id(level_id)

    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Level not found.",
        )

    await service.delete_level(level)

    return None