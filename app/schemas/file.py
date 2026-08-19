from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FileCreate(BaseModel):
    uploaded_by: UUID | None = None

    storage_path: str = Field(
        min_length=1,
    )

    original_filename: str = Field(
        min_length=1,
        max_length=255,
    )

    content_type: str | None = Field(
        default=None,
        max_length=100,
    )

    size: int = Field(
        ge=0,
    )

    is_deleted: bool = False


class FileUpdate(BaseModel):
    original_filename: str | None = Field(
        default=None,
        max_length=255,
    )

    content_type: str | None = Field(
        default=None,
        max_length=100,
    )

    size: int | None = Field(
        default=None,
        ge=0,
    )

    is_deleted: bool | None = None


class FileResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    uploaded_by: UUID | None
    storage_path: str
    original_filename: str
    content_type: str | None
    size: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class FileUploadResponse(BaseModel):
    id: UUID
    file_name: str
    file_url: str
    content_type: str | None
    size: int