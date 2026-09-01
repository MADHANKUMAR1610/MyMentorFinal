import uuid
from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    Float,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.database import Base
from app.models.base import (
    UUIDPrimaryKeyMixin,
    TimestampMixin,
)


class JobApplication(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "job_applications"

    # ============================================================
    # JOB
    # ============================================================

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "jobs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ============================================================
    # APPLICANT
    # ============================================================

    applicant_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # ============================================================
    # RECRUITER
    # ============================================================

    recruiter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # ============================================================
    # BASIC APPLICANT INFORMATION
    # ============================================================

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

    experience: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    cover_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    resume_link: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ============================================================
    # RECRUITMENT ANALYTICS
    # ============================================================

    # Where the candidate came from
    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    # ATS screening score
    ats_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        index=True,
    )

    # Job/candidate matching score
    match_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        index=True,
    )

    # ============================================================
    # RECRUITMENT PIPELINE TIMESTAMPS
    # ============================================================

    screened_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    shortlisted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    interviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    finalist_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    selected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    rejected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ============================================================
    # STATUS
    # ============================================================

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="submitted",
        index=True,
    )

    # ============================================================
    # RELATIONSHIPS
    # ============================================================

    recruiter = relationship(
        "User",
        foreign_keys=[recruiter_id],
    )

    applicant = relationship(
        "User",
        foreign_keys=[applicant_user_id],
    )