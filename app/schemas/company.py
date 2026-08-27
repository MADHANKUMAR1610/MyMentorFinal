from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ============================================================
# CREATE COMPANY
# ============================================================

class CompanyCreate(BaseModel):

    name: str

    industry: str

    logo: str | None = None

    website: str | None = None

    location: str | None = None

    size: str | None = None

    open_roles: int = 0

    about: str | None = None

    # --------------------------------------------------------
    # CONTACT PERSON
    # --------------------------------------------------------

    contact_person_name: str | None = None

    contact_email: str | None = None

    contact_phone: str | None = None

    contact_role: str | None = None

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status: str = "pending"

    verified: bool = False


# ============================================================
# COMPANY ONBOARDING
# ============================================================

class CompanyOnboardingCreate(BaseModel):

    # --------------------------------------------------------
    # STEP 1 - COMPANY PROFILE
    # --------------------------------------------------------

    name: str

    industry: str

    logo: str | None = None

    website: str | None = None

    location: str | None = None

    size: str | None = None

    open_roles: int = 0

    about: str | None = None

    # --------------------------------------------------------
    # STEP 2 - CONTACT PERSON
    # Google Login provides:
    # contact_person_name
    # contact_email
    # --------------------------------------------------------

    contact_person_name: str | None = None

    contact_email: str | None = None

    contact_phone: str | None = None

    contact_role: str | None = None

    # --------------------------------------------------------
    # STEP 3 - ADMIN CREDENTIAL
    # --------------------------------------------------------

    admin_official_email: str | None = None

    password: str | None = None


# ============================================================
# UPDATE COMPANY
# ============================================================

class CompanyUpdate(BaseModel):

    name: str | None = None

    industry: str | None = None

    logo: str | None = None

    website: str | None = None

    location: str | None = None

    size: str | None = None

    open_roles: int | None = None

    about: str | None = None

    # --------------------------------------------------------
    # CONTACT PERSON
    # --------------------------------------------------------

    contact_person_name: str | None = None

    contact_email: str | None = None

    contact_phone: str | None = None

    contact_role: str | None = None

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status: str | None = None

    verified: bool | None = None


# ============================================================
# COMPANY RESPONSE
# ============================================================

class CompanyResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID

    # --------------------------------------------------------
    # COMPANY PROFILE
    # --------------------------------------------------------

    name: str

    industry: str

    logo: str | None

    location: str | None

    size: str | None

    open_roles: int

    about: str | None

    website: str | None

    # --------------------------------------------------------
    # COMPANY STATUS
    # --------------------------------------------------------

    status: str

    verified: bool

    # --------------------------------------------------------
    # CONTACT PERSON
    # --------------------------------------------------------

    contact_person_name: str | None

    contact_email: str | None

    contact_phone: str | None

    contact_role: str | None

    # --------------------------------------------------------
    # ADMIN USER
    # --------------------------------------------------------

    admin_user_id: UUID | None

    # --------------------------------------------------------
    # TIMESTAMPS
    # --------------------------------------------------------

    created_at: datetime

    updated_at: datetime