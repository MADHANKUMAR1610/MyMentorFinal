from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(
    BaseRepository[Notification]
):

    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(
            Notification,
            session,
        )

    # ============================================================
    # GET USER NOTIFICATIONS
    # ============================================================

    async def get_by_user_id(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Notification]:

        result = await self.session.execute(
            select(Notification)
            .where(
                Notification.user_id == user_id
            )
            .order_by(
                Notification.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    # ============================================================
    # GET COMPANY NOTIFICATIONS
    # ============================================================

    async def get_by_company_id(
        self,
        company_id: UUID,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Notification]:

        result = await self.session.execute(
            select(Notification)
            .where(
                Notification.company_id == company_id
            )
            .order_by(
                Notification.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    # ============================================================
    # GET UNREAD COUNT
    # ============================================================

    async def get_unread_count(
        self,
        user_id: UUID,
    ) -> int:

        from sqlalchemy import func

        result = await self.session.execute(
            select(
                func.count(Notification.id)
            )
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
        )

        return result.scalar() or 0

    # ============================================================
    # GET NOTIFICATION
    # ============================================================

    async def get_user_notification(
        self,
        notification_id: UUID,
        user_id: UUID,
    ) -> Notification | None:

        result = await self.session.execute(
            select(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # MARK ONE AS READ
    # ============================================================

    async def mark_as_read(
        self,
        notification: Notification,
    ) -> Notification:

        notification.is_read = True

        await self.session.flush()

        await self.session.refresh(
            notification
        )

        return notification

    # ============================================================
    # MARK ALL AS READ
    # ============================================================

    async def mark_all_as_read(
        self,
        user_id: UUID,
    ) -> int:

        result = await self.session.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .values(
                is_read=True
            )
        )

        await self.session.flush()

        return result.rowcount or 0

    # ============================================================
    # DELETE NOTIFICATION
    # ============================================================

    async def delete_notification(
        self,
        notification: Notification,
    ) -> None:

        await self.session.delete(
            notification
        )

        await self.session.flush()