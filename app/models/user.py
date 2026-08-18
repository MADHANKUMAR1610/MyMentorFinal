from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class User(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "users"

    email: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True,
    )

    google_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=True,
    )

    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        default="",
    )

    role: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="student",
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    xp: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    streak: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    last_active: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    onboarded: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    career_persona = relationship(
        "CareerPersona",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )