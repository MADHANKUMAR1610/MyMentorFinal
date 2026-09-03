from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_current_user,
)

from app.database.database import get_db

from app.models.user import User

from app.schemas.notification import (
    NotificationListResponse,
    NotificationResponse,
)

from app.services.notification_service import (
    NotificationService,
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


# ============================================================
# GET NOTIFICATIONS
# ============================================================

@router.get(
    "",
    response_model=NotificationListResponse,
)
async def get_notifications(
    skip: int = Query(
        0,
        ge=0,
    ),
    limit: int = Query(
        50,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):

    service = NotificationService(db)

    notifications, unread_count = (
        await service.get_user_notifications(
            current_user.id,
            skip=skip,
            limit=limit,
        )
    )

    return NotificationListResponse(
        notifications=[
            NotificationResponse.model_validate(
                notification
            )
            for notification in notifications
        ],
        unread_count=unread_count,
        total=len(notifications),
    )


# ============================================================
# GET UNREAD COUNT
# ============================================================

@router.get(
    "/unread-count",
)
async def get_unread_count(
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):

    service = NotificationService(db)

    unread_count = (
        await service.get_unread_count(
            current_user.id
        )
    )

    return {
        "unread_count": unread_count
    }


# ============================================================
# MARK ONE AS READ
# ============================================================

@router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
async def mark_notification_as_read(
    notification_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):

    service = NotificationService(db)

    notification = (
        await service.mark_as_read(
            notification_id,
            current_user.id,
        )
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )

    return NotificationResponse.model_validate(
        notification
    )


# ============================================================
# MARK ALL AS READ
# ============================================================

@router.put(
    "/read-all",
)
async def mark_all_notifications_as_read(
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):

    service = NotificationService(db)

    updated_count = (
        await service.mark_all_as_read(
            current_user.id
        )
    )

    return {
        "message": "All notifications marked as read.",
        "updated_count": updated_count,
    }


# ============================================================
# DELETE NOTIFICATION
# ============================================================

@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_notification(
    notification_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):

    service = NotificationService(db)

    deleted = await service.delete(
        notification_id,
        current_user.id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )

    return None
# ============================================================
# TEST NOTIFICATION
# ============================================================

@router.post(
    "/test",
    response_model=NotificationResponse,
)
async def create_test_notification(
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):

    service = NotificationService(db)

    notification = (
        await service.create_notification(
            user_id=current_user.id,
            company_id=current_user.company_id,
            title="New applications",
            message="61 candidates have applied across active jobs.",
            notification_type="application",
        )
    )

    return NotificationResponse.model_validate(
        notification
    )