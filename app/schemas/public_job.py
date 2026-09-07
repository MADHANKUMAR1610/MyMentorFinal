from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PublicJobListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_code: str
    company_id: UUID | None = None

    title: str
    company_name: str
    location: str | None = None
    job_type: str
    work_mode: str | None = None

    experience: str | None = None
    min_experience: int | None = None
    max_experience: int | None = None

    salary: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None

    skills: list[str] = []
    required_skills: list[str] = []

    summary: str | None = None
    description: str | None = None

    applicants: int
    status: str
    created_at: datetime


class PublicJobListResponse(BaseModel):
    items: list[PublicJobListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
    
class PublicJobDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_code: str
    company_id: UUID | None = None

    title: str
    company_name: str
    location: str | None = None
    job_type: str
    work_mode: str | None = None

    # Experience
    experience: str | None = None
    min_experience: int | None = None
    max_experience: int | None = None

    # Salary
    salary: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None

    # Skills
    skills: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)

    # JD content
    summary: str | None = None
    description: str | None = None
    responsibilities: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    preferred_qualifications: list[str] = Field(default_factory=list)
    education: str | None = None
    applicants: int
    status: str
    created_at: datetime