from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
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
from app.schemas.course_enrollment import (
    CourseEnrollmentResponse,
)
from app.services.course_enrollment_service import (
    CourseEnrollmentService,
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
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
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
            detail=(
                "A course with this title "
                "already exists."
            ),
        )

    course = Course(
        title=data.title,
        description=data.description,
        category=data.category,
        language=data.language,
        difficulty=data.difficulty,
        duration=data.duration,
        thumbnail=data.thumbnail,
        status=data.status,
        certificate_template=(
            data.certificate_template
        ),
    )

    created_course = await service.create_course(
        course
    )

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
    category: str | None = Query(
        default=None,
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
    session: AsyncSession = Depends(
        get_db
    ),
):
    """
    Get courses with optional filters.

    Optional filters:
    - status
    - category
    - language
    - difficulty
    """

    service = CourseService(session)

    rows = await service.get_courses_with_level_count(
        course_status=course_status,
        category=category,
        language=language,
        difficulty=difficulty,
        skip=skip,
        limit=limit,
    )

    return [
        CourseResponse(
            **CourseResponse.model_validate(
                course
            ).model_dump(
                exclude={
                    "level_count",
                    "enrollment_count",
                }
            ),
            level_count=level_count,
            enrollment_count=enrollment_count,
        )
        for course, level_count, enrollment_count
        in rows
    ]


# ============================================================
# GET MY ENROLLMENTS
# ============================================================

@router.get(
    "/my-enrollments",
    response_model=list[
        CourseEnrollmentResponse
    ],
)
async def get_my_enrollments(
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):
    """
    Get all courses enrolled by the
    authenticated user.
    """

    service = CourseEnrollmentService(
        session
    )

    rows = await service.get_my_enrollments(
        user_id=current_user.id
    )

    return [
        CourseEnrollmentResponse(
            id=enrollment.id,
            course_id=course.id,
            title=course.title,
            description=course.description,
            category=course.category,
            language=course.language,
            difficulty=course.difficulty,
            duration=course.duration,
            thumbnail=course.thumbnail,
            enrolled_at=enrollment.enrolled_at,
        )
        for enrollment, course in rows
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
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):
    """
    Get a course by UUID.
    """

    service = CourseService(session)

    course = await service.get_by_id(
        course_id
    )

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found.",
        )

    return CourseResponse.model_validate(
        course
    )


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
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):
    """
    Update a course.
    """

    service = CourseService(session)

    course = await service.get_by_id(
        course_id
    )

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found.",
        )

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    if data.title is not None:

        existing_course = (
            await service.get_by_title(
                data.title
            )
        )

        if (
            existing_course is not None
            and existing_course.id != course.id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A course with this title "
                    "already exists."
                ),
            )

        course.title = data.title

    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    if data.description is not None:
        course.description = data.description

    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    if data.category is not None:
        course.category = data.category

    # --------------------------------------------------------
    # LANGUAGE
    # --------------------------------------------------------

    if data.language is not None:
        course.language = data.language

    # --------------------------------------------------------
    # DIFFICULTY
    # --------------------------------------------------------

    if data.difficulty is not None:
        course.difficulty = data.difficulty

    # --------------------------------------------------------
    # DURATION
    # --------------------------------------------------------

    if data.duration is not None:
        course.duration = data.duration

    # --------------------------------------------------------
    # THUMBNAIL
    # --------------------------------------------------------

    if data.thumbnail is not None:
        course.thumbnail = data.thumbnail

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if data.status is not None:
        course.status = data.status

    # --------------------------------------------------------
    # CERTIFICATE TEMPLATE
    # --------------------------------------------------------

    if data.certificate_template is not None:
        course.certificate_template = (
            data.certificate_template
        )

    updated_course = (
        await service.update_course(
            course
        )
    )

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
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):
    """
    Delete a course.
    """

    service = CourseService(session)

    course = await service.get_by_id(
        course_id
    )

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found.",
        )

    await service.delete_course(
        course
    )

    return None


# ============================================================
# ENROLL IN COURSE
# ============================================================

@router.post(
    "/{course_id}/enroll",
    response_model=CourseEnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def enroll_in_course(
    course_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):
    """
    Enroll the authenticated user
    in a course.
    """

    service = CourseEnrollmentService(
        session
    )

    try:

        enrollment = (
            await service.enroll_user(
                user_id=current_user.id,
                course_id=course_id,
            )
        )

        await session.commit()

        # ----------------------------------------------------
        # Get course details
        # ----------------------------------------------------

        course = (
            await service.course_repository.get_by_id(
                course_id
            )
        )

        return CourseEnrollmentResponse(
            id=enrollment.id,
            course_id=course.id,
            title=course.title,
            description=course.description,
            category=course.category,
            language=course.language,
            difficulty=course.difficulty,
            duration=course.duration,
            thumbnail=course.thumbnail,
            enrolled_at=enrollment.enrolled_at,
        )

    except ValueError as exc:

        await session.rollback()

        message = str(exc)

        if message == "Course not found.":

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        if (
            message
            == "You are already enrolled in this course."
        ):

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )