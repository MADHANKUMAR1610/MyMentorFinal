from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class MentorApplication(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "mentor_applications"

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    role: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    company: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    industry: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    experience_years: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    languages: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    linkedin: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    motivation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
        index=True,
    )