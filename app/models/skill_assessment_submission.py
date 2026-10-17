
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SkillAssessmentSubmission(Base):
    __tablename__ = "skill_assessment_submissions"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "question_id",
            name="uq_skill_assessment_user_question",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    question_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "skill_assessment_questions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    passed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    points_earned: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
