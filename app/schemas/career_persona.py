# app/schemas/career_persona.py

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# CREATE CAREER PERSONA
# ============================================================

class CareerPersonaCreate(BaseModel):

    goal: str

    answers: dict[str, Any] = Field(
        default_factory=dict
    )


# ============================================================
# UPDATE CAREER PERSONA
# ============================================================

class CareerPersonaUpdate(BaseModel):

    goal: str | None = None

    profile: dict[str, Any] | None = None

    answers: dict[str, Any] | None = None

    result: dict[str, Any] | None = None


# ============================================================
# CAREER PERSONA RESPONSE
# ============================================================

class CareerPersonaResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID

    user_id: UUID

    goal: str

    profile: dict[str, Any]

    answers: dict[str, Any]

    result: dict[str, Any]


# ============================================================
# CAREER PERSONA FLOW RESPONSE
# ============================================================

class CareerPersonaFlowResponse(BaseModel):

    requires_class_selection: bool

    career_persona: CareerPersonaResponse | None = None