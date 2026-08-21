from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.career_calendar import (
    CareerCalendarCreate,
    CareerCalendarResponse,
    CourseSuggestionResponse,
)
from app.services.career_calendar_service import (
    CareerCalendarService,
)


router = APIRouter(
    prefix="/career-persona",
    tags=["Career Persona"],
)


# ============================================================
# ADD TO CAREER CALENDAR
# ============================================================

@router.post(
    "/calendar",
    response_model=CareerCalendarResponse,
    status_code=status.HTTP_200_OK,
)
async def add_to_career_calendar(
    data: CareerCalendarCreate,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CareerCalendarService(session)

    try:

        calendar = await service.add_to_calendar(
            user_id=current_user.id,
            career_persona_id=data.career_persona_id,
            add_to_calendar=data.add_to_calendar,
        )

        return CareerCalendarResponse.model_validate(
            calendar
        )

    except ValueError as exc:

        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except PermissionError as exc:

        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


# ============================================================
# GET COURSE SUGGESTIONS
# ============================================================

@router.get(
    "/course-suggestions",
    response_model=list[CourseSuggestionResponse],
)
async def get_course_suggestions(
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CareerCalendarService(session)

    try:

        courses = (
            await service.get_course_suggestions(
                user_id=current_user.id
            )
        )

        return [
            CourseSuggestionResponse(
                id=course.id,
                title=course.title,
                description=course.description,
                language=course.language,
                difficulty=course.difficulty,
                duration=course.duration,
                thumbnail=course.thumbnail,
                enrolled=enrolled,
            )
            for course, enrolled in courses
        ]

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )