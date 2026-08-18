from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class Company(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    industry: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    logo: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    size: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    open_roles: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    about: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    website: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
        index=True,
    )

    verified: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )