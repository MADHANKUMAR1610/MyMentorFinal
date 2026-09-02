from uuid import UUID
from pydantic import BaseModel, ConfigDict


class OrganizationJobListItem(BaseModel):
    id: UUID
    job_id: str
    title: str
    department: str | None = None
    location: str | None = None
    employment_type: str | None = None

    experience_min: int | None = None
    experience_max: int | None = None

    applications_count: int = 0
    matched_count: int = 0
    shortlisted_count: int = 0
    interviews_count: int = 0
    selected_count: int = 0

    status: str

    model_config = ConfigDict(from_attributes=True)


class OrganizationJobListResponse(BaseModel):
    items: list[OrganizationJobListItem]
    total: int
    page: int
    page_size: int
    total_pages: int