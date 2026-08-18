from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CareerPersonaCreate(BaseModel):
    goal: str
    profile: dict[str, Any] = {}
    answers: dict[str, Any] = {}
    result: dict[str, Any] = {}


class CareerPersonaUpdate(BaseModel):
    goal: str | None = None
    profile: dict[str, Any] | None = None
    answers: dict[str, Any] | None = None
    result: dict[str, Any] | None = None


class CareerPersonaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    goal: str
    profile: dict[str, Any]
    answers: dict[str, Any]
    result: dict[str, Any]