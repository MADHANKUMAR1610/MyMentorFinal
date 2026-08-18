from datetime import datetime
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
    """
    Create a booking for the currently authenticated user.
    """

    mentor = await session.get(
        Mentor,
        data.mentor_id,
    )

    if mentor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor not found.",
        )

    if mentor.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This mentor is not available for booking.",
        )

    booking = Booking(
        mentor_id=data.mentor_id,
        user_id=current_user.id,
        scheduled_at=data.scheduled_at,
        topic=data.topic,
        mode=data.mode,
        meeting_link=data.meeting_link,
        status=data.status,
        report=data.report,
    )

    service = BookingService(session)

    created_booking = await service.create_booking(
        booking
    )

    return BookingResponse.model_validate(
        created_booking
    )


# ============================================================
# GET MY BOOKINGS
# ============================================================

@router.get(
    "/me",
    response_model=list[BookingResponse],
)
async def get_my_bookings(
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
    Get bookings belonging to the current user.
    """

    service = BookingService(session)

    bookings = await service.get_by_user_id(
        current_user.id,
        skip=skip,
        limit=limit,
    )

    return [
        BookingResponse.model_validate(booking)
        for booking in bookings
    ]


# ============================================================
# GET UPCOMING MY BOOKINGS
# ============================================================

@router.get(
    "/me/upcoming",
    response_model=list[BookingResponse],
)
async def get_my_upcoming_bookings(
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get upcoming bookings for the current user.
    """

    service = BookingService(session)

    bookings = await service.get_upcoming_for_user(
        current_user.id,
        limit=limit,
    )

    return [
        BookingResponse.model_validate(booking)
        for booking in bookings
    ]


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
    """
    Get a booking by ID.
    """

    service = BookingService(session)

    booking = await service.get_by_id(
        booking_id
    )

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

    return BookingResponse.model_validate(
        booking
    )


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
    """
    Update a booking belonging to the current user.
    """

    service = BookingService(session)

    booking = await service.get_by_id(
        booking_id
    )

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

    if data.scheduled_at is not None:
        booking.scheduled_at = data.scheduled_at

    if data.topic is not None:
        booking.topic = data.topic

    if data.mode is not None:
        booking.mode = data.mode

    if data.meeting_link is not None:
        booking.meeting_link = data.meeting_link

    if data.status is not None:
        booking.status = data.status

    if data.report is not None:
        booking.report = data.report

    updated_booking = await service.update_booking(
        booking
    )

    return BookingResponse.model_validate(
        updated_booking
    )


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
    """
    Delete a booking belonging to the current user.
    """

    service = BookingService(session)

    booking = await service.get_by_id(
        booking_id
    )

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

    await service.delete_booking(booking)

    return None