import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.models.base import (
    UUIDPrimaryKeyMixin,
    TimestampMixin,
)


class SkillAssessmentQuestion(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "skill_assessment_questions"

    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "skill_assessment_categories.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    question_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    problem: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    instructions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    language: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="Java",
    )

    difficulty: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="Beginner",
    )

    points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10,
    )

    starter_code: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    expected_answer: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    evaluation_criteria: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
    )