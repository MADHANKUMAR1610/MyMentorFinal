
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.booking import Booking
from app.models.mentor import Mentor
from app.models.user import User
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    BookingUpdate,
)
from app.services.booking_service import BookingService


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


# ============================================================
# CREATE BOOKING
# ============================================================

@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(
    data: BookingCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Create a booking for the authenticated user."""

    mentor = await session.get(Mentor, data.mentor_id)

    if mentor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor not found.",
        )

    booking = Booking(
        mentor_id=mentor.id,
        user_id=current_user.id,
        scheduled_at=data.scheduled_at,
        topic=data.topic,
        mode=data.mode,
        meeting_link=data.meeting_link,
        status="upcoming",
        report=None,
    )

    service = BookingService(session)

    try:
        return await service.create_booking(booking)
    except Exception:
        await session.rollback()
        raise


# ============================================================
# GET MY BOOKINGS
# ============================================================

@router.get(
    "/me",
    response_model=list[BookingResponse],
)
async def get_my_bookings(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = BookingService(session)

    return await service.get_by_user_id(
        current_user.id,
        skip=skip,
        limit=limit,
    )


# ============================================================
# GET UPCOMING MY BOOKINGS
# ============================================================

@router.get(
    "/me/upcoming",
    response_model=list[BookingResponse],
)
async def get_my_upcoming_bookings(
    limit: int = Query(default=100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = BookingService(session)

    return await service.get_upcoming_for_user(
        current_user.id,
        limit=limit,
    )


# ============================================================
# GET BOOKING BY ID
# ============================================================

@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
)
async def get_booking_by_id(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = BookingService(session)
    booking = await service.get_by_id(booking_id)

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found.",
        )

    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this booking.",
        )

    return booking


# ============================================================
# UPDATE MY BOOKING
# ============================================================

@router.put(
    "/{booking_id}",
    response_model=BookingResponse,
)
async def update_booking(
    booking_id: UUID,
    data: BookingUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = BookingService(session)
    booking = await service.get_by_id(booking_id)

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found.",
        )

    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this booking.",
        )

    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(booking, field, value)

    try:
        return await service.update_booking(booking)
    except Exception:
        await session.rollback()
        raise


# ============================================================
# DELETE MY BOOKING
# ============================================================

@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_booking(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = BookingService(session)
    booking = await service.get_by_id(booking_id)

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found.",
        )

    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this booking.",
        )

    try:
        await service.delete_booking(booking)
    except Exception:
        await session.rollback()
        raise

    return None
