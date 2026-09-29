from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.introduction_mcq import (
    IntroductionMCQSubmit,
    IntroductionMCQResponse,
)
from app.services.introduction_mcq_service import (
    IntroductionMCQService,
)


router = APIRouter(
    prefix="/introduction-mcqs",
    tags=["Introduction MCQs"],
)


@router.post(
    "/submit",
    response_model=IntroductionMCQResponse,
)
async def submit_introduction_mcq(
    data: IntroductionMCQSubmit,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = IntroductionMCQService(
        session
    )

    return await service.submit_mcq(
        user_id=current_user.id,
        level_id=data.level_id,
        question_index=data.question_index,
        selected_option=data.selected_option,
    )