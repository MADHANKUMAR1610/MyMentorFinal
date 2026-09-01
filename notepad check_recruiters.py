import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.job import Job
from app.models.job_application import JobApplication


async def main():

    async with AsyncSessionLocal() as db:

        # ---------------------------------------------
        # JOBS
        # ---------------------------------------------

        jobs_result = await db.execute(
            select(
                Job.id,
                Job.title,
                Job.recruiter_id,
                Job.company_id,
            )
        )

        jobs = jobs_result.all()

        print("\n================ JOBS ================\n")

        for job in jobs:
            print(
                "Job ID:",
                job.id,
                "| Title:",
                job.title,
                "| Recruiter ID:",
                job.recruiter_id,
                "| Company ID:",
                job.company_id,
            )

        # ---------------------------------------------
        # APPLICATIONS
        # ---------------------------------------------

        applications_result = await db.execute(
            select(
                JobApplication.id,
                JobApplication.job_id,
                JobApplication.recruiter_id,
                JobApplication.name,
                JobApplication.status,
            )
        )

        applications = applications_result.all()

        print("\n=========== APPLICATIONS ===========\n")

        for application in applications:
            print(
                "Application ID:",
                application.id,
                "| Job ID:",
                application.job_id,
                "| Recruiter ID:",
                application.recruiter_id,
                "| Name:",
                application.name,
                "| Status:",
                application.status,
            )


if __name__ == "__main__":
    asyncio.run(main())