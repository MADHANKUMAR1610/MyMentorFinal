from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MasterDataCreate(BaseModel):
    type: str = Field(
        min_length=1,
        max_length=50,
    )

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    year: int = Field(
        ge=2000,
        le=2100,
    )

    is_active: bool = True


class MasterDataUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    year: int | None = Field(
        default=None,
        ge=2000,
        le=2100,
    )

    is_active: bool | None = None


class MasterDataResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    type: str
    name: str
    year: int
    is_active: bool
    created_at: datetime
    updated_at: datetime