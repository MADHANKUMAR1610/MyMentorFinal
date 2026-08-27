from uuid import uuid4

from sqlalchemy import Boolean, Column, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database.database import Base


class CareerPersona(Base):
    __tablename__ = "career_personas"

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

    # ========================================================
    # RELATIONSHIP
    # ========================================================

    user = relationship(
        "User",
        back_populates="career_persona",
    )