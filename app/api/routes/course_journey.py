from uuid import UUID

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
from app.schemas.course_journey import (
    CourseJourneyResponse,
)
from app.services.course_journey_service import (
    CourseJourneyService,
)


router = APIRouter(
    prefix="/courses",
    tags=["Course Journey"],
)


# ============================================================
# GET COURSE JOURNEY
# ============================================================

@router.get(
    "/{course_id}/journey",
    response_model=CourseJourneyResponse,
)
async def get_course_journey(
    course_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):
    """
    Get the authenticated user's learning journey
    for a specific enrolled course.
    """

    service = CourseJourneyService(
        session
    )

    try:

        journey = (
            await service.get_course_journey(
                user_id=current_user.id,
                course_id=course_id,
            )
        )

        return journey

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except PermissionError as exc:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )