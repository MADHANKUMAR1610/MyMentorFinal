from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ============================================================
# NOTIFICATION RESPONSE
# ============================================================

class NotificationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID

    user_id: UUID

    company_id: UUID | None = None

    title: str

    message: str

    type: str

    is_read: bool

    created_at: datetime


# ============================================================
# NOTIFICATION LIST RESPONSE
# ============================================================

class NotificationListResponse(BaseModel):

    notifications: list[NotificationResponse]

    unread_count: int

    total: int