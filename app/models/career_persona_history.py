from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func


from app.database.database import Base


class CareerPersonaHistory(Base):
    __tablename__ = "career_persona_history"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    career_persona_id = Column(
        UUID(as_uuid=True),
        ForeignKey("career_personas.id"),
        nullable=True,
    )

    goal = Column(
        Text,
        nullable=False,
    )

    profile = Column(
        JSONB,
        default=dict,
        nullable=False,
    )

    answers = Column(
        JSONB,
        default=dict,
        nullable=False,
    )

    result = Column(
        JSONB,
        default=dict,
        nullable=False,
    )

    is_profile_visible = Column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )