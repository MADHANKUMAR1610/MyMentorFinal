from pydantic import BaseModel


class OrganizationJobSummaryResponse(BaseModel):

    total_jobs: int

    draft: int

    active: int

    paused: int

    closed: int

    filled: int