import uuid
from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Text,
    Numeric,
    DateTime,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.models.base import (
    UUIDPrimaryKeyMixin,
    TimestampMixin,
)


class Job(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "jobs"

    # ============================================================
    # JOB CODE
    # JOB-1001, JOB-1002, JOB-1003...
    # ============================================================

    job_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        server_default=text(
            "'JOB-' || nextval('public.job_code_seq')::text"
        ),
    )

    # ============================================================
    # ORGANIZATION
    # ============================================================

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

    recruiter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    hiring_manager_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ============================================================
    # BASIC INFORMATION
    # ============================================================

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    company_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    department: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        index=True,
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

    work_mode: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    min_experience: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    max_experience: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    openings: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    salary_min: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    salary_max: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    # ============================================================
    # RECRUITMENT ANALYTICS
    # ============================================================

    opened_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    required_skills: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
    )

    # ============================================================
    # OLD / COMPATIBILITY FIELDS
    # ============================================================

    experience: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    salary: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # ============================================================
    # JOB DESCRIPTION
    # ============================================================

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    responsibilities: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
    )

    preferred_skills: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
    )

    education: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    skills: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
    )

    apply_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # ============================================================
    # REQUIREMENTS
    # ============================================================

    mandatory_requirements: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
    )

    preferred_requirements: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
    )

    # ============================================================
    # SCREENING QUESTIONS
    # ============================================================

    screening_questions: Mapped[list[dict]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    # ============================================================
    # ATS CONFIGURATION
    # ============================================================

    ats_configuration: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    # ============================================================
    # APPLICATION / STATUS
    # ============================================================

    applicants: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="draft",
        index=True,
    )