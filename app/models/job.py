import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class Job(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "jobs"

    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    posted_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    company_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    job_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Full-time",
    )

    experience: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    salary: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    skills: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    apply_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    applicants: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="open",
        index=True,
    )