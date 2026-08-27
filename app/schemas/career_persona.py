from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ============================================================
# CREATE
# ============================================================

class CareerPersonaCreate(BaseModel):

    goal: str

    answers: dict[str, Any] = {}


# ============================================================
# UPDATE
# ============================================================

class CareerPersonaUpdate(BaseModel):

    goal: Optional[str] = None

    profile: Optional[dict[str, Any]] = None

    answers: Optional[dict[str, Any]] = None

    result: Optional[dict[str, Any]] = None


# ============================================================
# RESPONSE
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

    is_profile_visible: bool


# ============================================================
# GENERATE FLOW RESPONSE
# ============================================================

class CareerPersonaFlowResponse(BaseModel):

    requires_class_selection: bool

    career_persona: CareerPersonaResponse

    show_profile_confirmation: bool

    profile_confirmation_message: str


# ============================================================
# PROFILE RESPONSE
# ============================================================

class CareerPersonaProfileResponse(BaseModel):

    message: str

    profile_visible: bool

    career_persona: CareerPersonaResponse