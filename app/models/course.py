from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class Course(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "courses"

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Programming",
        index=True,
    )

    language: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Python",
    )

    difficulty: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Beginner",
    )

    duration: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    thumbnail: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="draft",
        index=True,
    )

    certificate_template: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )