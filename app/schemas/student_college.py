from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================
# COLLEGE CODE REQUEST
# ============================================================

class StudentCollegeCodeRequest(BaseModel):

    college_code: str = Field(
        ...,
        min_length=2,
        max_length=50,
    )


# ============================================================
# COLLEGE RESPONSE
# ============================================================

class StudentCollegeResponse(BaseModel):

    id: UUID
    name: str
    code: str
    college_type: str | None = None
    city: str
    state: str
    country: str
    status: str