from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.database.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.journey_service import JourneyService


security = HTTPBearer()


def get_journey_service(
    session: AsyncSession = Depends(get_db),
) -> JourneyService:
    return JourneyService(session)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db),
) -> User:

    token = credentials.credentials

    user_id: UUID | None = decode_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    repository = UserRepository(session)

    user = await repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:

    if current_user.role not in ["admin", "company_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    return current_user


async def get_current_system_admin(
    current_user: User = Depends(get_current_user),
) -> User:

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System admin access required.",
        )

    return current_user


async def get_current_company_admin(
    current_user: User = Depends(get_current_user),
) -> User:

    if current_user.role != "company_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company admin access required.",
        )

    if current_user.company_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company admin is not linked to a company.",
        )

    return current_user