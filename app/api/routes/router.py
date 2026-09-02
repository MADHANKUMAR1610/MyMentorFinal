from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.profiles import router as profiles_router
from app.api.routes.career_personas import (
    router as career_personas_router,
)
from app.api.routes.audit_logs import (
    router as audit_logs_router,
)
from app.api.routes.mentors import router as mentors_router
from app.api.routes.mentor_applications import (
    router as mentor_applications_router,
)
from app.api.routes.bookings import router as bookings_router
from app.api.routes import dashboard

from app.api.routes.companies import (
    router as companies_router,
)

from app.api.routes.company_applications import (
    router as company_applications_router,
)

from app.api.routes.jobs import (
    router as jobs_router,
)

from app.api.routes.job_applications import (
    router as job_applications_router,
)

from app.api.routes.courses import (
    router as courses_router,
)
from app.api.routes.organizations import (
    router as organizations_router,
)


from app.api.routes.levels import (
    router as levels_router,
)

from app.api.routes.checkpoints import (
    router as checkpoints_router,
)

from app.api.routes.progress import (
    router as progress_router,
)

from app.api.routes.master_data import (
    router as master_data_router,
)

from app.api.routes.files import (
    router as files_router,
)

from app.api.routes.journey import (
    router as journey_router,
)

from app.api.routes.course_journey import (
    router as course_journey_router,
)

from app.api.routes.career_calendar import (
    router as career_calendar_router,
)

from app.api.routes.work_experience import (
    router as work_experience_router,
)

from app.api.routes.code_execution import (
    router as code_execution_router,
)
from app.api.routes.organization_applications import (
    router as organization_applications_router,
)
from app.api.routes.organization_member import (
    router as organization_member_router,
)
from app.api.routes.interview import (
    router as interview_router,
)
from app.api.routes.organization_analytics import (
    router as organization_analytics_router,
)
from app.api.routes.organization_dashboard import (
    router as organization_dashboard_router,
)
# ============================================================
# MAIN API ROUTER
# ============================================================

api_router = APIRouter()


# ============================================================
# COURSE JOURNEY
# ============================================================

api_router.include_router(
    course_journey_router
)


# ============================================================
# CAREER CALENDAR
# ============================================================

api_router.include_router(
    career_calendar_router
)


# ============================================================
# CODE EXECUTION
# ============================================================

api_router.include_router(
    code_execution_router
)


# ============================================================
# JOURNEY
# ============================================================

api_router.include_router(
    journey_router
)


# ============================================================
# AUTH
# ============================================================

api_router.include_router(
    auth_router
)


# ============================================================
# MASTER DATA
# ============================================================

api_router.include_router(
    master_data_router
)


# ============================================================
# USERS
# ============================================================

api_router.include_router(
    users_router
)
api_router.include_router(
    audit_logs_router
)


# ============================================================
# FILES
# ============================================================

api_router.include_router(
    files_router
)


# ============================================================
# PROFILES
# ============================================================

api_router.include_router(
    profiles_router
)


# ============================================================
# CAREER PERSONAS
# ============================================================

api_router.include_router(
    career_personas_router
)


# ============================================================
# MENTORS
# ============================================================

api_router.include_router(
    mentors_router
)


# ============================================================
# WORK EXPERIENCE
# ============================================================

api_router.include_router(
    work_experience_router
)


# ============================================================
# MENTOR APPLICATIONS
# ============================================================

api_router.include_router(
    mentor_applications_router
)


# ============================================================
# BOOKINGS
# ============================================================

api_router.include_router(
    bookings_router
)


# ============================================================
# COMPANIES
# ============================================================

api_router.include_router(
    companies_router
)


# ============================================================
# COMPANY ONBOARDING
# ============================================================


# ============================================================
# COMPANY APPLICATIONS
# ============================================================

api_router.include_router(
    company_applications_router
)


# ============================================================
# DASHBOARD
# ============================================================

api_router.include_router(
    dashboard.router
)


# ============================================================
# JOBS
# ============================================================

api_router.include_router(
    jobs_router
)


# ============================================================
# JOB APPLICATIONS
# ============================================================

api_router.include_router(
    job_applications_router
)


# ============================================================
# COURSES
# ============================================================

api_router.include_router(
    courses_router
)

api_router.include_router(organizations_router)

api_router.include_router(
    organization_applications_router
)

api_router.include_router(
    organization_member_router
)

api_router.include_router(
    interview_router
)
api_router.include_router(
    organization_analytics_router
)
api_router.include_router(
    organization_dashboard_router
)