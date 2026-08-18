import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class Checkpoint(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "checkpoints"

    level_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("levels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    checkpoint_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    at_seconds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    scenario: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    problem_statement: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    objective: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    difficulty: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="Easy",
    )

    marks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=25,
    )

    xp: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=25,
    )

    retry_limit: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
    )

    language: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="python",
    )

    starter_code: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    constraints: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    hints: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    solution: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    visible_test_cases: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    hidden_test_cases: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )