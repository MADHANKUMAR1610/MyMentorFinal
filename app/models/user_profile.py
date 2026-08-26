import uuid
from datetime import date

from sqlalchemy import Date, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class UserProfile(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "user_profiles"

    # =========================================================
    # USER
    # =========================================================

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # =========================================================
    # PROFILE PHOTO
    # =========================================================

    profile_photo_file_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("files.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # =========================================================
    # PROFILE PHOTO RELATIONSHIP
    # =========================================================

    profile_photo = relationship(
        "File",
        foreign_keys=[profile_photo_file_id],
        lazy="joined",
    )

    # =========================================================
    # BASIC PROFILE
    # =========================================================

    dob: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    age: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    profile_category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    education: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    class_year: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    institution: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    career_goal: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    career_interests: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

        # =========================================================
    # WORK EXPERIENCES
    # =========================================================

    work_experiences = relationship(
        "WorkExperience",
        back_populates="user_profile",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # =========================================================
    # USER RELATIONSHIP
    # =========================================================

    user = relationship(
        "User",
        back_populates="profile",
    )