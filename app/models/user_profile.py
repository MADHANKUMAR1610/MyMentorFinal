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

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

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

    user = relationship(
        "User",
        back_populates="profile",
    )