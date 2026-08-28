from uuid import UUID

from pydantic import BaseModel


class OrganizationDashboardStats(BaseModel):
    total_jobs: int = 0
    active_jobs: int = 0
    total_applications: int = 0
    shortlisted_candidates: int = 0


class OrganizationDashboardResponse(BaseModel):
    organization_id: UUID
    organization_name: str
    industry: str
    logo: str | None = None
    verified: bool

    stats: OrganizationDashboardStats