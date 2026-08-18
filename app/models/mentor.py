from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class Mentor(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "mentors"

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
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
        index=True,
    )

    image_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    experience_years: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    languages: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    skills: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
    )

    rating: Mapped[float] = mapped_column(
        Numeric(3, 2),
        nullable=False,
        default=0,
    )

    price: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    availability: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
        index=True,
    )

    verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )