from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================
# COLLEGE CODE REQUEST
# ============================================================




class StudentCodeRequest(BaseModel):
    student_code: str = Field(
        ...,
        min_length=5,
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