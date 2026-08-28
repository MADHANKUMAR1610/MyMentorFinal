from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict
from typing import Literal



class OrganizationJobStatusUpdate(BaseModel):
    status: Literal["open", "closed"]

class OrganizationJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    company_name: str
    location: str | None = None
    job_type: str
    experience: str | None = None
    salary: str | None = None
    skills: list[str]
    description: str
    apply_email: str | None = None
    applicants: int
    status: str
    created_at: datetime
class OrganizationJobCreate(BaseModel):
    title: str
    location: str | None = None
    job_type: str = "Full-time"
    experience: str | None = None
    salary: str | None = None
    skills: list[str] = []
    description: str
    apply_email: str | None = None
class OrganizationJobUpdate(BaseModel):
    title: str | None = None
    location: str | None = None
    job_type: str | None = None
    experience: str | None = None
    salary: str | None = None
    skills: list[str] | None = None
    description: str | None = None
    apply_email: str | None = None
    status: str | None = None