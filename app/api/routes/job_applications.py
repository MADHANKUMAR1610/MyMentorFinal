
from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.job_application import JobApplication
from app.schemas.job_application import (
    JobApplicationCreate,
    JobApplicationUpdate,
    JobApplicationResponse,
    JobApplicationStatusUpdate,
    JobApplicationStatsResponse,
)
from app.services.job_application_service import JobApplicationService
from app.services.job_service import JobService


router = APIRouter(
    prefix="/job-applications",
    tags=["Job Applications"],
)


async def get_job_application_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobApplicationService:
    return JobApplicationService(db)


async def get_job_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobService:
    return JobService(db)


def application_response(
    service: JobApplicationService,
    application: JobApplication,
) -> JobApplicationResponse:
    return service.build_application_response(application)


def application_responses(
    service: JobApplicationService,
    applications: list[JobApplication],
) -> list[JobApplicationResponse]:
    return [
        service.build_application_response(application)
        for application in applications
    ]


# ============================================================
# CREATE APPLICATION
# ============================================================

@router.post(
    "",
    response_model=JobApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_application(
    data: JobApplicationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    application_service: Annotated[
        JobApplicationService,
        Depends(get_job_application_service),
    ],
    job_service: Annotated[
        JobService,
        Depends(get_job_service),
    ],
):
    if str(current_user.role).lower() != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only student accounts can submit job applications.",
        )

    if not current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your account must have an email address.",
        )

    job = await job_service.get_by_id(data.job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    if hasattr(job, "is_active") and not job.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This job is no longer accepting applications.",
        )

    application = JobApplication(
        job_id=data.job_id,
        applicant_user_id=current_user.id,
        name=current_user.name,
        email=current_user.email.strip().lower(),
        phone=data.phone,
        experience=data.experience,
        cover_note=data.cover_note,
        resume_file_id=data.resume_file_id,
        resume_source=data.resume_source,
        resume_link=str(data.resume_link) if data.resume_link else None,
    )

    try:
        created = await application_service.submit_application(application)
        return application_response(application_service, created)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# GET MY APPLICATIONS
# ============================================================

@router.get(
    "/me",
    response_model=list[JobApplicationResponse],
)
async def get_my_applications(
    current_user: Annotated[User, Depends(get_current_user)],
    application_service: Annotated[
        JobApplicationService,
        Depends(get_job_application_service),
    ],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    applications = await application_service.get_by_applicant_user_id(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    return application_responses(application_service, applications)


# ============================================================
# GET APPLICATIONS BY STATUS
# ============================================================

@router.get(
    "/recruiter/status",
    response_model=list[JobApplicationResponse],
)
async def get_applications_by_status(
    current_user: Annotated[User, Depends(get_current_user)],
    application_service: Annotated[
        JobApplicationService,
        Depends(get_job_application_service),
    ],
    application_status: str = Query(..., alias="status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    if str(current_user.role).lower() not in {
        "recruiter",
        "organization_admin",
        "hiring_manager",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view recruiter applications.",
        )

    try:
        applications = await application_service.get_by_status(
            status=application_status,
            skip=skip,
            limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return application_responses(application_service, applications)


# ============================================================
# GET APPLICATION BY ID
# ============================================================

@router.get(
    "/{application_id}",
    response_model=JobApplicationResponse,
)
async def get_application_by_id(
    application_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    application_service: Annotated[
        JobApplicationService,
        Depends(get_job_application_service),
    ],
):
    application = await application_service.get_by_id(application_id)

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found.",
        )

    if application.applicant_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this application.",
        )

    return application_response(application_service, application)


# ============================================================
# UPDATE MY APPLICATION
# ============================================================

@router.patch(
    "/{application_id}",
    response_model=JobApplicationResponse,
)
async def update_application(
    application_id: UUID,
    data: JobApplicationUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    application_service: Annotated[
        JobApplicationService,
        Depends(get_job_application_service),
    ],
):
    application = await application_service.get_by_id(application_id)

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found.",
        )

    if application.applicant_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this application.",
        )

    if application.status in {"selected", "rejected", "withdrawn"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This application can no longer be updated.",
        )

    update_data = data.model_dump(exclude_unset=True)

    for field in (
        "id",
        "job_id",
        "applicant_user_id",
        "recruiter_id",
        "status",
        "ats_score",
        "match_score",
    ):
        update_data.pop(field, None)

    if "email" in update_data and update_data["email"]:
        update_data["email"] = update_data["email"].strip().lower()

    if "resume_link" in update_data:
        update_data["resume_link"] = (
            str(update_data["resume_link"])
            if update_data["resume_link"]
            else None
        )

    # Update only fields allowed by the schema.
    for field, value in update_data.items():
        if hasattr(application, field):
            setattr(application, field, value)

    updated_application = await application_service.repository.update(
        application
    )

    return application_response(application_service, updated_application)


# ============================================================
# WITHDRAW APPLICATION
# ============================================================

@router.delete(
    "/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def withdraw_application(
    application_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    application_service: Annotated[
        JobApplicationService,
        Depends(get_job_application_service),
    ],
):
    application = await application_service.get_by_id(application_id)

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found.",
        )

    if application.applicant_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to withdraw this application.",
        )

    if application.status in {"selected", "rejected"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected or rejected applications cannot be withdrawn.",
        )

    application.status = "withdrawn"
    await application_service.repository.update(application)

    return None


# ============================================================
# GET APPLICATIONS BY COMPANY
# ============================================================

@router.get(
    "/recruiter/company/{company_id}",
    response_model=list[JobApplicationResponse],
)
async def get_applications_by_company(
    company_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    application_service: Annotated[
        JobApplicationService,
        Depends(get_job_application_service),
    ],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    if str(current_user.role).lower() not in {
        "recruiter",
        "organization_admin",
        "hiring_manager",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view company applications.",
        )

    if getattr(current_user, "company_id", None) != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access another company's applications.",
        )

    applications = await application_service.get_by_company_id(
        company_id=company_id,
        skip=skip,
        limit=limit,
    )

    return application_responses(application_service, applications)


# ============================================================
# UPDATE APPLICATION STATUS
# ============================================================

@router.patch(
    "/recruiter/{application_id}/status",
    response_model=JobApplicationResponse,
)
async def update_application_status(
    application_id: UUID,
    data: JobApplicationStatusUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    application_service: Annotated[
        JobApplicationService,
        Depends(get_job_application_service),
    ],
):
    if str(current_user.role).lower() not in {
        "recruiter",
        "organization_admin",
        "hiring_manager",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update application status.",
        )

    application = await application_service.get_by_id(application_id)

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found.",
        )

    company_id = getattr(current_user, "company_id", None)

    if company_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not associated with a company.",
        )

    try:
        updated_application = (
            await application_service.update_organization_application_status(
                application_id=application_id,
                company_id=company_id,
                new_status=data.status,
                performed_by_user_id=current_user.id,
                performed_by_name=getattr(current_user, "name", "") or "",
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if updated_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found for your company.",
        )

    return application_response(application_service, updated_application)


# ============================================================
# APPLICATION STATISTICS
# ============================================================

@router.get(
    "/recruiter/stats/{company_id}",
    response_model=JobApplicationStatsResponse,
)
async def get_application_stats(
    company_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    application_service: Annotated[
        JobApplicationService,
        Depends(get_job_application_service),
    ],
):
    if str(current_user.role).lower() not in {
        "recruiter",
        "organization_admin",
        "hiring_manager",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view application statistics.",
        )

    if getattr(current_user, "company_id", None) != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access another company's statistics.",
        )

    return await application_service.get_company_application_stats(
        company_id
    )
