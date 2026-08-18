import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class CompanyApplication(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "company_applications"

    company_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    website: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    industry: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    contact_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    size: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    about: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    hiring_needs: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    submitted_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
        index=True,
    )