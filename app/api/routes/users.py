from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get the currently authenticated user's profile.
    """

    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
)
async def update_my_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Update the currently authenticated user's profile.
    """

    service = UserService(session)

    if data.name is not None:
        current_user.name = data.name

    if data.phone is not None:
        existing_phone = await service.get_by_phone(data.phone)

        if (
            existing_phone is not None
            and existing_phone.id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this phone number already exists.",
            )

        current_user.phone = data.phone

    updated_user = await service.update_user(current_user)

    return UserResponse.model_validate(updated_user)
@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user_by_id(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get a user by UUID.
    """

    service = UserService(session)

    user = await service.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return UserResponse.model_validate(user)