from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrganizationUpdate(BaseModel):
    name: str | None = None
    industry: str | None = None
    logo: str | None = None
    location: str | None = None
    size: str | None = None
    about: str | None = None
    website: str | None = None

    contact_person_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    contact_role: str | None = None


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    industry: str
    logo: str | None = None
    location: str | None = None
    size: str | None = None
    open_roles: int

    about: str | None = None
    website: str | None = None

    status: str
    verified: bool

    contact_person_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    contact_role: str | None = None