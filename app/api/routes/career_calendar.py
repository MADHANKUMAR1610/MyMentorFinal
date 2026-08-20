# app/api/routes/career_calendar.py

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db

from app.models.user import User
from app.models.career_calendar import CareerCalendar

from app.schemas.career_calendar import (
    CareerCalendarCreate,
    CareerCalendarResponse,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/career-calendar",
    tags=["Career Calendar"],
)


# ============================================================
# CREATE CAREER CALENDAR
# ============================================================

@router.post(
    "/me",
    response_model=CareerCalendarResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_career_calendar(
    data: CareerCalendarCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    calendar = CareerCalendar(
        user_id=current_user.id,
        career_persona_id=data.career_persona_id,
        title=data.title,
        description=data.description,
        start_date=data.start_date,
        end_date=data.end_date,
    )

    session.add(calendar)

    await session.commit()

    await session.refresh(calendar)

    return CareerCalendarResponse.model_validate(calendar)


# ============================================================
# GET MY CAREER CALENDAR
# ============================================================

@router.get(
    "/me",
    response_model=list[CareerCalendarResponse],
)
async def get_my_career_calendar(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(CareerCalendar)
        .where(
            CareerCalendar.user_id == current_user.id
        )
        .order_by(
            CareerCalendar.start_date
        )
    )

    calendars = result.scalars().all()

    return [
        CareerCalendarResponse.model_validate(calendar)
        for calendar in calendars
    ]


# ============================================================
# GET CAREER CALENDAR BY ID
# ============================================================

@router.get(
    "/{calendar_id}",
    response_model=CareerCalendarResponse,
)
async def get_career_calendar(
    calendar_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(CareerCalendar)
        .where(
            CareerCalendar.id == calendar_id,
            CareerCalendar.user_id == current_user.id,
        )
    )

    calendar = result.scalar_one_or_none()

    if calendar is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career calendar not found.",
        )

    return CareerCalendarResponse.model_validate(calendar)


# ============================================================
# DELETE CAREER CALENDAR
# ============================================================

@router.delete(
    "/{calendar_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_career_calendar(
    calendar_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(CareerCalendar)
        .where(
            CareerCalendar.id == calendar_id,
            CareerCalendar.user_id == current_user.id,
        )
    )

    calendar = result.scalar_one_or_none()

    if calendar is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career calendar not found.",
        )

    await session.delete(calendar)

    await session.commit()

    return None