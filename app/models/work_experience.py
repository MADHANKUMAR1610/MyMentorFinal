import uuid
from datetime import date

from sqlalchemy import Date, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class WorkExperience(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "work_experiences"

    # =========================================================
    # USER PROFILE
    # =========================================================

    user_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_profiles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # =========================================================
    # COMPANY DETAILS
    # =========================================================

    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    job_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    employment_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # =========================================================
    # WORK PERIOD
    # =========================================================

    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    currently_working: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    # =========================================================
    # ADDITIONAL DETAILS
    # =========================================================

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # =========================================================
    # RELATIONSHIP
    # =========================================================

    user_profile = relationship(
        "UserProfile",
        back_populates="work_experiences",
    )