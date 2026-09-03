import uuid
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.repositories.notification_repository import (
    NotificationRepository,
)


class NotificationService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

        self.repository = (
            NotificationRepository(session)
        )

    # ============================================================
    # CREATE NOTIFICATION
    # ============================================================

    async def create_notification(
        self,
        *,
        user_id: UUID,
        company_id: UUID | None,
        title: str,
        message: str,
        notification_type: str = "system",
    ) -> Notification:

        notification = Notification(
            id=uuid.uuid4(),
            user_id=user_id,
            company_id=company_id,
            title=title,
            message=message,
            type=notification_type,
            is_read=False,
        )

        return await self.repository.create(
            notification
        )

    # ============================================================
    # GET USER NOTIFICATIONS
    # ============================================================

    async def get_user_notifications(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Notification], int]:

        notifications = (
            await self.repository.get_by_user_id(
                user_id,
                skip=skip,
                limit=limit,
            )
        )

        unread_count = (
            await self.repository.get_unread_count(
                user_id
            )
        )

        return notifications, unread_count

    # ============================================================
    # GET UNREAD COUNT
    # ============================================================

    async def get_unread_count(
        self,
        user_id: UUID,
    ) -> int:

        return await self.repository.get_unread_count(
            user_id
        )

    # ============================================================
    # MARK ONE AS READ
    # ============================================================

    async def mark_as_read(
        self,
        notification_id: UUID,
        user_id: UUID,
    ) -> Notification | None:

        notification = (
            await self.repository.get_user_notification(
                notification_id,
                user_id,
            )
        )

        if notification is None:
            return None

        return await self.repository.mark_as_read(
            notification
        )

    # ============================================================
    # MARK ALL AS READ
    # ============================================================

    async def mark_all_as_read(
        self,
        user_id: UUID,
    ) -> int:

        return await self.repository.mark_all_as_read(
            user_id
        )

    # ============================================================
    # DELETE
    # ============================================================

    async def delete(
        self,
        notification_id: UUID,
        user_id: UUID,
    ) -> bool:

        notification = (
            await self.repository.get_user_notification(
                notification_id,
                user_id,
            )
        )

        if notification is None:
            return False

        await self.repository.delete_notification(
            notification
        )

        return True