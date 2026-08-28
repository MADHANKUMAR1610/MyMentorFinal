from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db

from app.schemas.interview import (
    InterviewCreate,
    InterviewResponse,
    InterviewUpdate,
    InterviewStatusUpdate,
    InterviewFeedbackUpdate,
)

from app.services.interview_service import (
    InterviewService,
)


router = APIRouter(
    prefix="/organizations/me/interviews",
    tags=["Interview Management"],
)


# ============================================================
# CREATE / SCHEDULE INTERVIEW
# ============================================================


@router.post(
    "",
    response_model=InterviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_interview(
    data: InterviewCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = InterviewService(db)

    interview = await service.create_interview(
    user_id=current_user.id,
    application_id=data.application_id,
    interviewer_id=data.interviewer_id,
    title=data.title,
    interview_type=data.interview_type,
    scheduled_at=data.scheduled_at,
    duration_minutes=data.duration_minutes,
    mode=data.mode,
    meeting_link=data.meeting_link,
    location=data.location,
    notes=data.notes,
)

    return InterviewResponse.model_validate(
        interview
    )
# ============================================================
# GET ALL INTERVIEWS
# ============================================================

@router.get(
    "",
    response_model=list[InterviewResponse],
)
async def get_interviews(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all interviews belonging to the
    current user's organization.
    """

    service = InterviewService(db)

    interviews = await service.get_interviews(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    return [
        InterviewResponse.model_validate(
            interview
        )
        for interview in interviews
    ]


# ============================================================
# GET SINGLE INTERVIEW
# ============================================================

@router.get(
    "/{interview_id}",
    response_model=InterviewResponse,
)
async def get_interview(
    interview_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific interview belonging to
    the current user's organization.
    """

    service = InterviewService(db)

    interview = await service.get_interview(
        user_id=current_user.id,
        interview_id=interview_id,
    )

    return InterviewResponse.model_validate(
        interview
    )


# ============================================================
# UPDATE INTERVIEW
# ============================================================

@router.put(
    "/{interview_id}",
    response_model=InterviewResponse,
)
async def update_interview(
    interview_id: UUID,
    data: InterviewUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update interview details.
    """

    service = InterviewService(db)

    update_data = data.model_dump(
        exclude_unset=True
    )

    interview = await service.update_interview(
        user_id=current_user.id,
        interview_id=interview_id,
        data=update_data,
    )

    return InterviewResponse.model_validate(
        interview
    )


# ============================================================
# DELETE / CANCEL INTERVIEW
# ============================================================

@router.delete(
    "/{interview_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_interview(
    interview_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an interview from the organization.
    """

    service = InterviewService(db)

    await service.delete_interview(
        user_id=current_user.id,
        interview_id=interview_id,
    )

    return None


# ============================================================
# UPDATE INTERVIEW STATUS
# ============================================================

@router.put(
    "/{interview_id}/status",
    response_model=InterviewResponse,
)
async def update_interview_status(
    interview_id: UUID,
    data: InterviewStatusUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update interview status.

    Example:
    scheduled
    completed
    cancelled
    rescheduled
    no_show
    """

    service = InterviewService(db)

    interview = await service.update_interview_status(
        user_id=current_user.id,
        interview_id=interview_id,
        status=data.status,
    )

    return InterviewResponse.model_validate(
        interview
    )


@router.put(
    "/{interview_id}/feedback",
    response_model=InterviewResponse,
)
async def update_interview_feedback(
    interview_id: UUID,
    data: InterviewFeedbackUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = InterviewService(db)

    interview = await service.update_feedback(
        user_id=current_user.id,
        interview_id=interview_id,
        rating=data.rating,
        feedback=data.feedback,
        recommendation=data.recommendation,
        notes=data.notes,
    )

    return InterviewResponse.model_validate(interview)