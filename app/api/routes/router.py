from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.profiles import router as profiles_router
from app.api.routes.career_personas import router as career_personas_router
from app.api.routes.mentors import router as mentors_router
from app.api.routes.mentor_applications import (
    router as mentor_applications_router,
)
from app.api.routes.bookings import router as bookings_router
from app.api.routes import dashboard
api_router = APIRouter()
from app.api.routes.companies import router as companies_router
from app.api.routes.company_applications import (
    router as company_applications_router,
)
from app.api.routes.jobs import router as jobs_router
from app.api.routes.job_applications import (
    router as job_applications_router,
)
from app.api.routes.courses import router as courses_router
from app.api.routes.levels import router as levels_router
from app.api.routes.checkpoints import (
    router as checkpoints_router,
)
from app.api.routes.progress import router as progress_router
from app.api.routes.master_data import router as master_data_router
from app.api.routes.files import router as files_router
from app.api.routes.journey import router as journey_router

api_router.include_router(
    journey_router
)
api_router.include_router(auth_router)
api_router.include_router(master_data_router)
api_router.include_router(users_router)
api_router.include_router(files_router)
api_router.include_router(profiles_router)
api_router.include_router(career_personas_router)
api_router.include_router(mentors_router)
api_router.include_router(
    mentor_applications_router
)
api_router.include_router(bookings_router)
api_router.include_router(companies_router)
api_router.include_router(
    company_applications_router
    
)
api_router.include_router(dashboard.router)
api_router.include_router(jobs_router)
api_router.include_router(
    job_applications_router
)
api_router.include_router(courses_router)
api_router.include_router(levels_router)
api_router.include_router(
    checkpoints_router
)
api_router.include_router(progress_router)
