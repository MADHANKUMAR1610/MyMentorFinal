import uuid

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class OrganizationATSConfig(Base):
    __tablename__ = "organization_ats_config"

    # ========================================================
    # PRIMARY KEY
    # ========================================================

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ========================================================
    # COMPANY
    # ========================================================

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "companies.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        index=True,
    )

    company = relationship(
        "Company",
        foreign_keys=[company_id],
    )

    # ========================================================
    # ATS WEIGHTS
    # ========================================================

    skills: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30,
    )

    experience: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=20,
    )

    education: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=15,
    )

    role_relevance: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=20,
    )

    screening_questions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10,
    )

    certifications: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
    )