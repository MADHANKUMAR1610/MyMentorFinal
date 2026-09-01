from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ============================================================
# JOB STATUS
# ============================================================

JobStatus = Literal[
    "draft",
    "open",
    "closed",
]


# ============================================================
# ATS CONFIGURATION
# ============================================================

class ATSConfiguration(BaseModel):
    skills: int = Field(default=30, ge=0, le=100)
    experience: int = Field(default=20, ge=0, le=100)
    education: int = Field(default=15, ge=0, le=100)
    role_relevance: int = Field(default=20, ge=0, le=100)
    screening_questions: int = Field(default=10, ge=0, le=100)
    certifications: int = Field(default=5, ge=0, le=100)

    @model_validator(mode="after")
    def validate_total_weight(self):
        total = (
            self.skills
            + self.experience
            + self.education
            + self.role_relevance
            + self.screening_questions
            + self.certifications
        )

        if total != 100:
            raise ValueError(
                f"ATS weights must total 100%. Current total: {total}%"
            )

        return self


# ============================================================
# SCREENING QUESTION
# ============================================================

class ScreeningQuestion(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=1000,
    )

    question_type: str = "text"

    required: bool = True

    options: list[str] = Field(
        default_factory=list
    )


# ============================================================
# CREATE / PUBLISH JOB
# ============================================================

class OrganizationJobCreate(BaseModel):

    # --------------------------------------------------------
    # BASIC INFORMATION
    # --------------------------------------------------------

    title: str = Field(
        min_length=2,
        max_length=200,
    )

    department: str | None = Field(
        default=None,
        max_length=150,
    )

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    job_type: str = Field(
        default="Full-time",
        max_length=50,
    )

    work_mode: str = Field(
        default="On-site",
        max_length=50,
    )

    min_experience: int | None = Field(
        default=None,
        ge=0,
    )

    max_experience: int | None = Field(
        default=None,
        ge=0,
    )

    openings: int = Field(
        default=1,
        ge=1,
    )

    salary_min: float | None = Field(
        default=None,
        ge=0,
    )

    salary_max: float | None = Field(
        default=None,
        ge=0,
    )

    recruiter_id: UUID | None = None

    hiring_manager_id: UUID | None = None

    # --------------------------------------------------------
    # JOB DESCRIPTION
    # --------------------------------------------------------

    summary: str | None = None

    description: str | None = None

    responsibilities: list[str] = Field(
        default_factory=list
    )

    required_skills: list[str] = Field(
        default_factory=list
    )

    preferred_skills: list[str] = Field(
        default_factory=list
    )

    education: str | None = Field(
        default=None,
        max_length=150,
    )

    # --------------------------------------------------------
    # REQUIREMENTS
    # --------------------------------------------------------

    mandatory_requirements: list[str] = Field(
        default_factory=list
    )

    preferred_requirements: list[str] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # SCREENING QUESTIONS
    # --------------------------------------------------------

    screening_questions: list[ScreeningQuestion] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # ATS CONFIGURATION
    # --------------------------------------------------------

    ats_configuration: ATSConfiguration = Field(
        default_factory=ATSConfiguration
    )

    # --------------------------------------------------------
    # EXISTING FIELDS
    # --------------------------------------------------------

    apply_email: str | None = None

    status: JobStatus = "draft"

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    @model_validator(mode="after")
    def validate_ranges(self):

        if (
            self.min_experience is not None
            and self.max_experience is not None
            and self.min_experience > self.max_experience
        ):
            raise ValueError(
                "Minimum experience cannot be greater than maximum experience"
            )

        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError(
                "Minimum salary cannot be greater than maximum salary"
            )

        return self


# ============================================================
# UPDATE JOB
# ============================================================

class OrganizationJobUpdate(BaseModel):

    # --------------------------------------------------------
    # BASIC INFORMATION
    # --------------------------------------------------------

    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    department: str | None = Field(
        default=None,
        max_length=150,
    )

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    job_type: str | None = Field(
        default=None,
        max_length=50,
    )

    work_mode: str | None = Field(
        default=None,
        max_length=50,
    )

    min_experience: int | None = Field(
        default=None,
        ge=0,
    )

    max_experience: int | None = Field(
        default=None,
        ge=0,
    )

    openings: int | None = Field(
        default=None,
        ge=1,
    )

    salary_min: float | None = Field(
        default=None,
        ge=0,
    )

    salary_max: float | None = Field(
        default=None,
        ge=0,
    )

    recruiter_id: UUID | None = None

    hiring_manager_id: UUID | None = None

    # --------------------------------------------------------
    # JOB DESCRIPTION
    # --------------------------------------------------------

    summary: str | None = None

    description: str | None = None

    responsibilities: list[str] | None = None

    required_skills: list[str] | None = None

    preferred_skills: list[str] | None = None

    education: str | None = Field(
        default=None,
        max_length=150,
    )

    # --------------------------------------------------------
    # REQUIREMENTS
    # --------------------------------------------------------

    mandatory_requirements: list[str] | None = None

    preferred_requirements: list[str] | None = None

    # --------------------------------------------------------
    # SCREENING QUESTIONS
    # --------------------------------------------------------

    screening_questions: list[ScreeningQuestion] | None = None

    # --------------------------------------------------------
    # ATS CONFIGURATION
    # --------------------------------------------------------

    ats_configuration: ATSConfiguration | None = None

    # --------------------------------------------------------
    # EXISTING FIELDS
    # --------------------------------------------------------

    apply_email: str | None = None

    status: JobStatus | None = None

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    @model_validator(mode="after")
    def validate_ranges(self):

        if (
            self.min_experience is not None
            and self.max_experience is not None
            and self.min_experience > self.max_experience
        ):
            raise ValueError(
                "Minimum experience cannot be greater than maximum experience"
            )

        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError(
                "Minimum salary cannot be greater than maximum salary"
            )

        return self


# ============================================================
# STATUS UPDATE
# ============================================================

class OrganizationJobStatusUpdate(BaseModel):

    status: Literal[
        "draft",
        "open",
        "closed",
    ]


# ============================================================
# JOB RESPONSE
# ============================================================

class OrganizationJobResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID

    company_id: UUID | None

    posted_by: UUID | None

    title: str

    company_name: str

    department: str | None = None

    location: str | None = None

    job_type: str

    work_mode: str | None = None

    min_experience: int | None = None

    max_experience: int | None = None

    openings: int

    salary_min: float | None = None

    salary_max: float | None = None

    recruiter_id: UUID | None = None

    hiring_manager_id: UUID | None = None

    summary: str | None = None

    description: str | None = None

    responsibilities: list[str]

    required_skills: list[str]

    preferred_skills: list[str]

    education: str | None = None

    mandatory_requirements: list[str]

    preferred_requirements: list[str]

    screening_questions: list[dict]

    ats_configuration: dict

    # Existing fields

    skills: list[str]

    apply_email: str | None = None

    applicants: int

    status: str

    created_at: datetime

    updated_at: datetime
# ============================================================
# SAVE JOB DRAFT
# ============================================================

class OrganizationJobDraftCreate(BaseModel):

    # Basic Information
    title: str | None = Field(
        default=None,
        max_length=200,
    )

    department: str | None = Field(
        default=None,
        max_length=150,
    )

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    job_type: str | None = Field(
        default="Full-time",
        max_length=50,
    )

    work_mode: str | None = Field(
        default="On-site",
        max_length=50,
    )

    min_experience: int | None = Field(
        default=None,
        ge=0,
    )

    max_experience: int | None = Field(
        default=None,
        ge=0,
    )

    openings: int | None = Field(
        default=1,
        ge=1,
    )

    salary_min: float | None = Field(
        default=None,
        ge=0,
    )

    salary_max: float | None = Field(
        default=None,
        ge=0,
    )

    recruiter_id: UUID | None = None

    hiring_manager_id: UUID | None = None

    # Job Description
    summary: str | None = None

    description: str | None = None

    responsibilities: list[str] = Field(
        default_factory=list
    )

    required_skills: list[str] = Field(
        default_factory=list
    )

    preferred_skills: list[str] = Field(
        default_factory=list
    )

    education: str | None = Field(
        default=None,
        max_length=150,
    )

    # Requirements
    mandatory_requirements: list[str] = Field(
        default_factory=list
    )

    preferred_requirements: list[str] = Field(
        default_factory=list
    )

    # Screening Questions
    screening_questions: list[ScreeningQuestion] = Field(
        default_factory=list
    )

    # ATS
    ats_configuration: ATSConfiguration = Field(
        default_factory=ATSConfiguration
    )

    # Existing
    apply_email: str | None = None