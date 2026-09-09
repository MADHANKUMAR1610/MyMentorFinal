from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_application import JobApplication
from app.repositories.job_application_repository import (
    JobApplicationRepository,
)
from app.services.audit_log_service import AuditLogService
from app.services.user_profile_service import UserProfileService
from app.schemas.job_application import JobApplicationResponse


# ============================================================
# ALLOWED APPLICATION STATUSES
# ============================================================

ALLOWED_APPLICATION_STATUSES = {
    "submitted",
    "screening",
    "shortlisted",
    "interview",
    "technical_round",
    "hr_round",
    "finalist",
    "selected",
    "rejected",
}


class JobApplicationService:
    """
    Service layer for job applications.

    Handles:
    - Application creation
    - Validation
    - Duplicate prevention
    - Resume resolution
    - Organization status updates
    - Audit logging
    - Response construction
    """

    def __init__(self, session: AsyncSession):
        self.session = session

        self.repository = JobApplicationRepository(session)

        self.audit_service = AuditLogService(session)

        self.user_profile_service = UserProfileService(session)

    # ============================================================
    # GET APPLICATION BY ID
    # ============================================================

    async def get_by_id(
        self,
        application_id: UUID,
    ) -> JobApplication | None:

        return await self.repository.get_by_id(
            application_id
        )

    # ============================================================
    # GET APPLICATIONS BY JOB
    # ============================================================

    async def get_by_job_id(
        self,
        job_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JobApplication]:

        return await self.repository.get_by_job_id(
            job_id,
            skip=skip,
            limit=limit,
        )

    # ============================================================
    # GET APPLICATIONS BY APPLICANT
    # ============================================================

    async def get_by_applicant_user_id(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JobApplication]:

        return await self.repository.get_by_applicant_user_id(
            user_id,
            skip=skip,
            limit=limit,
        )

    # ============================================================
    # GET APPLICATIONS BY EMAIL
    # ============================================================

    async def get_by_email(
        self,
        email: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JobApplication]:

        return await self.repository.get_by_email(
            email,
            skip=skip,
            limit=limit,
        )

    # ============================================================
    # GET APPLICATIONS BY STATUS
    # ============================================================

    async def get_by_status(
        self,
        status: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JobApplication]:

        if status not in ALLOWED_APPLICATION_STATUSES:
            raise ValueError(
                f"Invalid application status: {status}"
            )

        return await self.repository.get_by_status(
            status,
            skip=skip,
            limit=limit,
        )

    # ============================================================
    # GET APPLICATION BY JOB AND USER
    # ============================================================

    async def get_by_job_and_user(
        self,
        job_id: UUID,
        user_id: UUID,
    ) -> JobApplication | None:

        return await self.repository.get_by_job_and_user(
            job_id,
            user_id,
        )

    # ============================================================
    # CREATE APPLICATION
    # ============================================================

    async def create_application(
        self,
        application: JobApplication,
    ) -> JobApplication:

        return await self.submit_application(
            application
        )

    # ============================================================
    # UPDATE APPLICATION
    # ============================================================

    async def update_application(
        self,
        application: JobApplication,
    ) -> JobApplication:

        return await self.repository.update(
            application
        )

    # ============================================================
    # DELETE APPLICATION
    # ============================================================

    async def delete_application(
        self,
        application: JobApplication,
    ) -> None:

        await self.repository.delete(
            application
        )

    # ============================================================
    # SUBMIT APPLICATION
    # ============================================================

    async def submit_application(
        self,
        application: JobApplication,
    ) -> JobApplication:
        """
        Submit a new job application.

        Authenticated applicants are checked by user ID.
        Guest applicants are checked by email.
        """

        # --------------------------------------------------------
        # Validate email
        # --------------------------------------------------------

        if not application.email:
            raise ValueError(
                "Applicant email is required."
            )

        application.email = (
            application.email.strip().lower()
        )

        # --------------------------------------------------------
        # Validate status
        # --------------------------------------------------------

        if not application.status:
            application.status = "submitted"

        if (
            application.status
            not in ALLOWED_APPLICATION_STATUSES
        ):
            raise ValueError(
                f"Invalid application status: "
                f"{application.status}"
            )

        # --------------------------------------------------------
        # Check duplicate application
        # --------------------------------------------------------

        if application.applicant_user_id:

            existing_application = (
                await self.repository.get_by_job_and_user(
                    job_id=application.job_id,
                    user_id=application.applicant_user_id,
                )
            )

        else:

            existing_application = (
                await self.repository.get_by_job_and_email(
                    job_id=application.job_id,
                    email=application.email,
                )
            )

        if existing_application:
            raise ValueError(
                "You have already applied for this job."
            )

        # --------------------------------------------------------
        # Create application
        # --------------------------------------------------------

        created_application = (
            await self.repository.create(
                application
            )
        )

        return created_application

    # ============================================================
    # UPDATE ORGANIZATION APPLICATION STATUS
    # ============================================================

    async def update_organization_application_status(
        self,
        application_id: UUID,
        company_id: UUID,
        new_status: str,
        performed_by_user_id: UUID,
        performed_by_name: str,
    ) -> JobApplication | None:

        # --------------------------------------------------------
        # Validate status
        # --------------------------------------------------------

        if new_status not in ALLOWED_APPLICATION_STATUSES:
            raise ValueError(
                f"Invalid application status: {new_status}"
            )

        # --------------------------------------------------------
        # Get organization application
        # --------------------------------------------------------

        application = (
            await self.repository.get_organization_application(
                application_id=application_id,
                company_id=company_id,
            )
        )

        if application is None:
            return None

        # --------------------------------------------------------
        # Store old status
        # --------------------------------------------------------

        old_status = application.status

        # --------------------------------------------------------
        # Avoid unnecessary update
        # --------------------------------------------------------

        if old_status == new_status:
            return application

        # --------------------------------------------------------
        # Create audit log
        # --------------------------------------------------------

        await self.audit_service.log_candidate_stage_changed(
            company_id=company_id,
            performed_by_user_id=performed_by_user_id,
            performed_by_name=performed_by_name,
            application=application,
            old_status=old_status,
            new_status=new_status,
        )

        # --------------------------------------------------------
        # Update status
        # --------------------------------------------------------

        application.status = new_status

        await self.session.commit()

        await self.session.refresh(
            application
        )

        return application

    # ============================================================
    # ORGANIZATION - GET ALL APPLICATIONS
    # ============================================================

    async def get_by_company_id(
        self,
        company_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        name: str | None = None,
        email: str | None = None,
        job_id: UUID | None = None,
    ) -> list[JobApplication]:

        if (
            status is not None
            and status not in ALLOWED_APPLICATION_STATUSES
        ):
            raise ValueError(
                f"Invalid application status: {status}"
            )

        return await self.repository.get_by_company_id(
            company_id,
            skip=skip,
            limit=limit,
            status=status,
            name=name,
            email=email,
            job_id=job_id,
        )

    # ============================================================
    # ORGANIZATION - GET APPLICATIONS FOR A JOB
    # ============================================================

    async def get_by_organization_job(
        self,
        job_id: UUID,
        company_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JobApplication]:

        return await self.repository.get_by_organization_job(
            job_id=job_id,
            company_id=company_id,
            skip=skip,
            limit=limit,
        )

    # ============================================================
    # ORGANIZATION - GET SINGLE APPLICATION
    # ============================================================

    async def get_organization_application(
        self,
        application_id: UUID,
        company_id: UUID,
    ) -> JobApplication | None:

        return await self.repository.get_organization_application(
            application_id=application_id,
            company_id=company_id,
        )

    # ============================================================
    # ORGANIZATION - APPLICATION STATS
    # ============================================================

    async def get_company_application_stats(
        self,
        company_id: UUID,
    ) -> dict[str, int]:

        return await self.repository.get_company_application_stats(
            company_id
        )

    async def get_organization_application_stats(
        self,
        company_id: UUID,
    ) -> dict[str, int]:

        return await self.repository.get_status_counts_by_company_id(
            company_id
        )

    # ============================================================
    # BUILD APPLICATION RESPONSE
    # ============================================================

    def build_application_response(
        self,
        application: JobApplication,
    ) -> JobApplicationResponse:

        # --------------------------------------------------------
        # Resume URL
        # --------------------------------------------------------

        resume_url = application.resume_link

        if (
            application.resume_file
            and not application.resume_file.is_deleted
        ):
            resume_url = (
                application.resume_file.public_url
            )

        # --------------------------------------------------------
        # Response
        # --------------------------------------------------------

        return JobApplicationResponse(
            id=application.id,
            job_id=application.job_id,
            applicant_user_id=application.applicant_user_id,
            name=application.name,
            email=application.email,
            phone=application.phone,
            experience=application.experience,
            cover_note=application.cover_note,
            resume_file_id=application.resume_file_id,
            resume_source=application.resume_source,
            resume_link=application.resume_link,
            resume_url=resume_url,
            status=application.status,
            created_at=application.created_at,
            updated_at=application.updated_at,
        )

    # ============================================================
    # RESOLVE RESUME
    # ============================================================

    async def resolve_resume(
        self,
        applicant_user_id: UUID | None,
        resume_source: str,
        resume_file_id: UUID | None = None,
        resume_link: str | None = None,
    ) -> tuple[UUID | None, str | None]:
        """
        Resolve the resume selected during application submission.

        Supported sources:
        - profile: Use the applicant's saved profile resume.
        - new_upload: Use the newly uploaded resume file.
        """

        # ========================================================
        # PROFILE RESUME
        # ========================================================

        if resume_source == "profile":

            if not applicant_user_id:
                raise ValueError(
                    "Applicant user ID is required "
                    "for profile resume."
                )

            profile = (
                await self.user_profile_service.get_by_user_id(
                    applicant_user_id
                )
            )

            if profile is None:
                raise ValueError(
                    "User profile not found."
                )

            if not profile.resume_file_id:
                raise ValueError(
                    "No resume found in user profile."
                )

            if (
                profile.resume_file is None
                or profile.resume_file.is_deleted
            ):
                raise ValueError(
                    "Profile resume file is unavailable."
                )

            return (
                profile.resume_file_id,
                profile.resume_file.public_url,
            )

        # ========================================================
        # NEW UPLOAD
        # ========================================================

        if resume_source == "new_upload":

            if not resume_file_id:
                raise ValueError(
                    "Resume file is required "
                    "for new upload."
                )

            return (
                resume_file_id,
                resume_link,
            )

        # ========================================================
        # INVALID SOURCE
        # ========================================================

        raise ValueError(
            "Invalid resume source. "
            "Allowed values: profile, new_upload."
        )