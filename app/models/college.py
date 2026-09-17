import uuid

from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.models.base import (
    UUIDPrimaryKeyMixin,
    TimestampMixin,
)


class College(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "colleges"

    # ========================================================
    # BASIC COLLEGE DETAILS
    # ========================================================

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    college_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    established_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    university_affiliation: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    accreditation: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # ========================================================
    # CONTACT INFORMATION
    # ========================================================

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    website: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    principal_dean_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    contact_person: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    # ========================================================
    # ADDRESS
    # ========================================================

    address: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="India",
    )

    pincode: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )

    # ========================================================
    # ADDITIONAL INFORMATION
    # ========================================================

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="active",
        index=True,
    )