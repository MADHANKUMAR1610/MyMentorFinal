
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ============================================================
# HISTORY RESPONSE
# ============================================================

class CareerPersonaHistoryResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID

    user_id: UUID

    career_persona_id: UUID | None

    goal: str

    profile: dict[str, Any]

    answers: dict[str, Any]

    result: dict[str, Any]

    is_profile_visible: bool

    created_at: datetime


# ============================================================
# HISTORY LIST RESPONSE
# ============================================================

class CareerPersonaHistoryListResponse(BaseModel):

    items: list[CareerPersonaHistoryResponse]

    total: int

