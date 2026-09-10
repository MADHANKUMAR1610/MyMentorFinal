
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

from app.models.user import User

from app.schemas.career_persona_history import (
    CareerPersonaHistoryResponse,
    CareerPersonaHistoryListResponse,
)

from app.services.career_persona_history_service import (
    CareerPersonaHistoryService,
)


router = APIRouter(
    prefix="/career-persona-history",
    tags=["Career Persona History"],
)


# ============================================================
# GET ALL MY CAREER PERSONA HISTORY
# ============================================================

@router.get(
    "/me",
    response_model=CareerPersonaHistoryListResponse,
)
async def get_my_career_persona_history(
    skip: int = Query(
        0,
        ge=0,
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CareerPersonaHistoryService(
        session
    )

    history = await service.get_user_history(
        current_user.id,
        skip=skip,
        limit=limit,
    )

    total = await service.count_user_history(
        current_user.id
    )

    return CareerPersonaHistoryListResponse(
        items=[
            CareerPersonaHistoryResponse.model_validate(
                item
            )
            for item in history
        ],
        total=total,
    )


# ============================================================
# GET LATEST HISTORY
# IMPORTANT: THIS MUST COME BEFORE /{history_id}
# ============================================================

@router.get(
    "/me/latest",
    response_model=CareerPersonaHistoryResponse,
)
async def get_latest_career_persona_history(
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CareerPersonaHistoryService(
        session
    )

    history = await service.get_latest_by_user_id(
        current_user.id
    )

    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career persona history not found.",
        )

    return CareerPersonaHistoryResponse.model_validate(
        history
    )


# ============================================================
# GET HISTORY BY ID
# ============================================================

@router.get(
    "/me/{history_id}",
    response_model=CareerPersonaHistoryResponse,
)
async def get_my_career_persona_history_by_id(
    history_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CareerPersonaHistoryService(
        session
    )

    history = await service.get_by_id(
        history_id
    )

    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career persona history not found.",
        )

    if history.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have access to this "
                "career persona history."
            ),
        )

    return CareerPersonaHistoryResponse.model_validate(
        history
    )

