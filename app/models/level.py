import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class Level(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "levels"

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    stage: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    stage_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    level_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    global_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    objectives: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    xp: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
    )

    pass_percentage: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
    )

    duration: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    video: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    theory: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )