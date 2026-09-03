import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.models.base import UUIDPrimaryKeyMixin


class Notification(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "notifications"

    # ============================================================
    # USER
    # ============================================================

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ============================================================
    # COMPANY
    # ============================================================

    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "companies.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    # ============================================================
    # NOTIFICATION CONTENT
    # ============================================================

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Example:
    # application
    # interview
    # candidate
    # job
    # user
    # system

    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="system",
        index=True,
    )

    # ============================================================
    # READ STATUS
    # ============================================================

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    # ============================================================
    # CREATED TIME
    # ============================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )