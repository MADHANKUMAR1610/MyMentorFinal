from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.course import Course
from app.models.user import User
from app.schemas.course import (
    CourseCreate,
    CourseResponse,
    CourseUpdate,
)
from app.services.course_service import CourseService


router = APIRouter(
    prefix="/courses",
    tags=["Courses"],
)


# ============================================================
# CREATE COURSE
# ============================================================

@router.post(
    "",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_course(
    data: CourseCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Create a new course.
    """

    service = CourseService(session)

    existing_course = await service.get_by_title(
        data.title
    )

    if existing_course is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A course with this title already exists.",
        )

    course = Course(
        title=data.title,
        description=data.description,
        language=data.language,
        difficulty=data.difficulty,
        duration=data.duration,
        thumbnail=data.thumbnail,
        status=data.status,
        certificate_template=data.certificate_template,
    )

    created_course = await service.create_course(course)

    return CourseResponse.model_validate(
        created_course
    )


# ============================================================
# GET COURSES
# ============================================================

@router.get(
    "",
    response_model=list[CourseResponse],
)
async def get_courses(
    course_status: str | None = Query(
        default=None,
        alias="status",
    ),
    language: str | None = Query(
        default=None,
    ),
    difficulty: str | None = Query(
        default=None,
    ),
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
    Get courses using optional filters.
    """

    service = CourseService(session)

    if course_status is not None:
        courses = await service.get_by_status(
            course_status,
            skip=skip,
            limit=limit,
        )

    elif language is not None:
        courses = await service.get_by_language(
            language,
            skip=skip,
            limit=limit,
        )

    elif difficulty is not None:
        courses = await service.get_by_difficulty(
            difficulty,
            skip=skip,
            limit=limit,
        )

    else:
        courses = await service.get_published(
            skip=skip,
            limit=limit,
        )

    return [
        CourseResponse.model_validate(course)
        for course in courses
    ]


# ============================================================
# GET COURSE BY ID
# ============================================================

@router.get(
    "/{course_id}",
    response_model=CourseResponse,
)
async def get_course_by_id(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get a course by UUID.
    """

    service = CourseService(session)

    course = await service.get_by_id(course_id)

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found.",
        )

    return CourseResponse.model_validate(course)


# ============================================================
# UPDATE COURSE
# ============================================================

@router.put(
    "/{course_id}",
    response_model=CourseResponse,
)
async def update_course(
    course_id: UUID,
    data: CourseUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Update a course.
    """

    service = CourseService(session)

    course = await service.get_by_id(course_id)

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found.",
        )

    if data.title is not None:
        existing_course = await service.get_by_title(
            data.title
        )

        if (
            existing_course is not None
            and existing_course.id != course.id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A course with this title already exists.",
            )

        course.title = data.title

    if data.description is not None:
        course.description = data.description

    if data.language is not None:
        course.language = data.language

    if data.difficulty is not None:
        course.difficulty = data.difficulty

    if data.duration is not None:
        course.duration = data.duration

    if data.thumbnail is not None:
        course.thumbnail = data.thumbnail

    if data.status is not None:
        course.status = data.status

    if data.certificate_template is not None:
        course.certificate_template = (
            data.certificate_template
        )

    updated_course = await service.update_course(course)

    return CourseResponse.model_validate(
        updated_course
    )


# ============================================================
# DELETE COURSE
# ============================================================

@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_course(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Delete a course.
    """

    service = CourseService(session)

    course = await service.get_by_id(course_id)

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found.",
        )

    await service.delete_course(course)

    return None