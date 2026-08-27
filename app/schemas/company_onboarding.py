from pydantic import BaseModel, EmailStr, Field


class CompanyOnboardingCreate(BaseModel):
    # ========================================================
    # COMPANY
    # ========================================================

    name: str = Field(
        min_length=2,
        max_length=200,
    )

    industry: str = Field(
        min_length=1,
        max_length=100,
    )

    logo: str | None = None

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    size: str | None = Field(
        default=None,
        max_length=50,
    )

    open_roles: int = Field(
        default=0,
        ge=0,
    )

    about: str | None = None

    website: str = Field(
        min_length=5,
        max_length=255,
    )

    status: str = Field(
        default="pending",
        max_length=30,
    )

    verified: bool = False

    # ========================================================
    # CONTACT PERSON
    # ========================================================

    contact_person_name: str = Field(
        min_length=2,
        max_length=150,
    )

    contact_email: EmailStr

    contact_phone: str | None = Field(
        default=None,
        max_length=20,
    )

    contact_role: str | None = Field(
        default=None,
        max_length=100,
    )

    google_id: str = Field(
        min_length=1,
        max_length=255,
    )

    # ========================================================
    # COMPANY ADMIN
    # ========================================================

    admin_official_email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class CompanyOnboardingResponse(BaseModel):
    company_id: str
    admin_user_id: str

    company_name: str
    contact_person_name: str
    contact_email: EmailStr

    admin_official_email: EmailStr
    role: str

    message: str