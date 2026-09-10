import uuid

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Text,
    func,
)

from sqlalchemy.dialects.postgresql import (
    UUID,
    JSONB,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database.database import Base


class CareerSearchKnowledge(Base):

    __tablename__ = "career_search_knowledge"

    # ========================================================
    # ID
    # ========================================================

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ========================================================
    # NORMALIZED QUERY
    # ========================================================

    query: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
        index=True,
    )

    # ========================================================
    # SEARCH KEYWORDS / ALIASES
    # ========================================================

    keywords: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    # ========================================================
    # AI / CAREER RESULT
    # ========================================================

    result: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    # ========================================================
    # ACTIVE
    # ========================================================

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    # ========================================================
    # TIMESTAMPS
    # ========================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )