from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrganizationJobListResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID

    job_code: str | None = None

    title: str

    department: str | None = None

    location: str | None = None

    job_type: str | None = None

    min_experience: int | None = None

    max_experience: int | None = None

    applications: int = 0

    matched: int = 0

    shortlisted: int = 0

    interviews: int = 0

    selected: int = 0

    status: str