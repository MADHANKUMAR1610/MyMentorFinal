from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# CREATE USER PROFILE
# ============================================================

class UserProfileCreate(BaseModel):
    """
    Create a user profile.
    """

    dob: date | None = None

    age: int | None = Field(
        default=None,
        ge=0,
        le=120,
    )

    profile_category: str | None = Field(
        default=None,
        max_length=50,
    )

    education: str | None = Field(
        default=None,
        max_length=255,
    )

    class_year: str | None = Field(
        default=None,
        max_length=50,
    )

    institution: str | None = Field(
        default=None,
        max_length=255,
    )

    career_goal: str | None = Field(
        default=None,
        max_length=255,
    )

    career_interests: str | None = None

    # --------------------------------------------------------
    # PROFILE PHOTO
    # --------------------------------------------------------

    profile_photo_file_id: UUID | None = None


# ============================================================
# UPDATE USER PROFILE
# ============================================================

class UserProfileUpdate(BaseModel):
    """
    Update a user profile.
    """

    dob: date | None = None

    age: int | None = Field(
        default=None,
        ge=0,
        le=120,
    )

    profile_category: str | None = Field(
        default=None,
        max_length=50,
    )

    education: str | None = Field(
        default=None,
        max_length=255,
    )

    class_year: str | None = Field(
        default=None,
        max_length=50,
    )

    institution: str | None = Field(
        default=None,
        max_length=255,
    )

    career_goal: str | None = Field(
        default=None,
        max_length=255,
    )

    career_interests: str | None = None

    # --------------------------------------------------------
    # PROFILE PHOTO
    # --------------------------------------------------------

    profile_photo_file_id: UUID | None = None


# ============================================================
# USER PROFILE RESPONSE
# ============================================================

class UserProfileResponse(BaseModel):
    """
    User profile API response.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    user_id: UUID

    dob: date | None
    age: int | None
    profile_category: str | None
    education: str | None
    class_year: str | None
    institution: str | None
    career_goal: str | None
    career_interests: str | None

    # Profile photo
    profile_photo_file_id: UUID | None = None
    profile_photo_url: str | None = None

    created_at: datetime
    updated_at: datetime
class ProfileSummaryResponse(BaseModel):
    score: int

    badge: str

    name: str

    career_goal: str | None = None

    xp: int

    day_streak: int

    completed_levels: int

    total_levels: int

    applications: int


# ============================================================
# SCORE BREAKDOWN
# ============================================================

class ScoreBreakdownResponse(BaseModel):
    total_score: int

    max_score: int

    career_clarity: int

    career_clarity_max: int

    learning_progress: int

    learning_progress_max: int

    profile_completeness: int

    profile_completeness_max: int

    consistency: int

    consistency_max: int

    job_readiness: int

    job_readiness_max: int