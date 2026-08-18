import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class CareerPersona(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "career_personas"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    goal: Mapped[str] = mapped_column(
        nullable=False,
    )

    profile: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    answers: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    result: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    user = relationship(
        "User",
        back_populates="career_persona",
    )