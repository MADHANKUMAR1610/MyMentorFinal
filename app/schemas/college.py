from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


COLLEGE_TYPES = {
    "government",
    "private",
    "government_aided",
    "deemed_university",
    "autonomous",
}

COLLEGE_STATUSES = {
    "active",
    "inactive",
    "pending_verification",
}


# ============================================================
# CREATE COLLEGE
# ============================================================

class CollegeCreate(BaseModel):

    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )

    

    college_type: str | None = None

    established_year: int | None = Field(
        default=None,
        ge=1800,
        le=2100,
    )

    university_affiliation: str | None = Field(
        default=None,
        max_length=255,
    )

    accreditation: str | None = Field(
        default=None,
        max_length=255,
    )

    # --------------------------------------------------------
    # CONTACT
    # --------------------------------------------------------

    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
    )

    phone: str = Field(
        ...,
        min_length=7,
        max_length=20,
    )

    website: str | None = None

    principal_dean_name: str | None = Field(
        default=None,
        max_length=150,
    )

    contact_person: str | None = Field(
        default=None,
        max_length=150,
    )

    # --------------------------------------------------------
    # ADDRESS
    # --------------------------------------------------------

    address: str = Field(
        ...,
        min_length=5,
    )

    city: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    state: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    country: str = Field(
        default="India",
        max_length=100,
    )

    pincode: str = Field(
        ...,
        min_length=4,
        max_length=10,
    )

    # --------------------------------------------------------
    # ADDITIONAL
    # --------------------------------------------------------

    description: str | None = None

    status: str = "active"

    # ========================================================
    # VALIDATORS
    # ========================================================

    

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("college_type")
    @classmethod
    def validate_college_type(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip().lower()

        if value not in COLLEGE_TYPES:
            raise ValueError(
                "Invalid college type."
            )

        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:

        value = value.strip().lower()

        if value not in COLLEGE_STATUSES:
            raise ValueError(
                "Invalid college status."
            )

        return value


# ============================================================
# UPDATE COLLEGE
# ============================================================

class CollegeUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    code: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    college_type: str | None = None

    established_year: int | None = Field(
        default=None,
        ge=1800,
        le=2100,
    )

    university_affiliation: str | None = None

    accreditation: str | None = None

    email: str | None = None

    phone: str | None = None

    website: str | None = None

    principal_dean_name: str | None = None

    contact_person: str | None = None

    address: str | None = None

    city: str | None = None

    state: str | None = None

    country: str | None = None

    pincode: str | None = None

    description: str | None = None

    status: str | None = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str | None) -> str | None:

        if value is None:
            return None

        return value.strip().upper()

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:

        if value is None:
            return None

        return value.strip().lower()

    @field_validator("college_type")
    @classmethod
    def validate_college_type(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip().lower()

        if value not in COLLEGE_TYPES:
            raise ValueError(
                "Invalid college type."
            )

        return value

    @field_validator("status")
    @classmethod
    def validate_status(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip().lower()

        if value not in COLLEGE_STATUSES:
            raise ValueError(
                "Invalid college status."
            )

        return value


# ============================================================
# RESPONSE
# ============================================================

class CollegeResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    name: str

    code: str

    college_type: str | None

    established_year: int | None

    university_affiliation: str | None

    accreditation: str | None

    email: str

    phone: str

    website: str | None

    principal_dean_name: str | None

    contact_person: str | None

    address: str

    city: str

    state: str

    country: str

    pincode: str

    description: str | None

    status: str

    created_at: datetime

    updated_at: datetime