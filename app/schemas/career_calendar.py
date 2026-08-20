# app/schemas/career_calendar.py

from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ============================================================
# CREATE
# ============================================================

class CareerCalendarCreate(BaseModel):

    career_persona_id: UUID | None = None

    title: str

    description: str | None = None

    start_date: datetime | None = None

    end_date: datetime | None = None


# ============================================================
# UPDATE
# ============================================================

class CareerCalendarUpdate(BaseModel):

    title: str | None = None

    description: str | None = None

    start_date: datetime | None = None

    end_date: datetime | None = None


# ============================================================
# RESPONSE
# ============================================================

class CareerCalendarResponse(BaseModel):

    id: UUID

    user_id: UUID

    career_persona_id: UUID | None

    title: str

    description: str | None

    start_date: datetime | None

    end_date: datetime | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )