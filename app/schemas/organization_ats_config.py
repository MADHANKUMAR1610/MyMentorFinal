from uuid import UUID

from pydantic import BaseModel


class OrganizationATSConfigUpdate(BaseModel):
    skills: int
    experience: int
    education: int
    role_relevance: int
    screening_questions: int
    certifications: int


class OrganizationATSConfigResponse(BaseModel):
    id: UUID
    company_id: UUID
    skills: int
    experience: int
    education: int
    role_relevance: int
    screening_questions: int
    certifications: int

    model_config = {
        "from_attributes": True
    }