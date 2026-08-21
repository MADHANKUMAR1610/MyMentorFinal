from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_current_user,
    get_journey_service,
)
from app.models.user import User
from app.services.journey_service import JourneyService
from app.schemas.journey import JourneyResponse


router = APIRouter(
    prefix="/journey",
    tags=["Journey"],
)


@router.get(
    "",
    response_model=JourneyResponse,
)
async def get_my_journey(
    current_user: User = Depends(get_current_user),
    journey_service: JourneyService = Depends(
        get_journey_service
    ),
):
    """
    Get the current user's dynamic MyMentor journey.
    """

    return await journey_service.get_user_journey(
        user_id=current_user.id
    )