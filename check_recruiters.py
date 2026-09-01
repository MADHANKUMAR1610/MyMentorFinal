import asyncio

from sqlalchemy import select

from app.database.database import AsyncSessionLocal
from app.models.job import Job
from app.models.job_application import JobApplication


COMPANY_ID = "93d40f35-9ec9-45c9-b259-96081b2f276b"
RECRUITER_ID = "cd25be22-2128-4969-80ec-2064b3a96795"


async def main():

    async with AsyncSessionLocal() as db:

        # --------------------------------------------------------
        # ASSIGN RECRUITER TO JOBS
        # --------------------------------------------------------

        jobs_result = await db.execute(
            select(Job).where(
                Job.company_id == COMPANY_ID
            )
        )

        jobs = jobs_result.scalars().all()

        print("\n================ JOBS ================\n")

        for job in jobs:

            job.recruiter_id = RECRUITER_ID

            print(
                "Assigned recruiter to:",
                job.title,
                "| Recruiter ID:",
                RECRUITER_ID,
            )

        # --------------------------------------------------------
        # ASSIGN RECRUITER TO APPLICATIONS
        # --------------------------------------------------------

        applications_result = await db.execute(
            select(JobApplication)
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == COMPANY_ID
            )
        )

        applications = applications_result.scalars().all()

        print("\n=========== APPLICATIONS ===========\n")

        for application in applications:

            application.recruiter_id = RECRUITER_ID

            print(
                "Assigned recruiter to application:",
                application.id,
                "| Recruiter ID:",
                RECRUITER_ID,
            )

        # --------------------------------------------------------
        # SAVE
        # --------------------------------------------------------

        await db.commit()

        print("\n======================================")
        print("Recruiter assignment completed.")
        print("Recruiter ID:", RECRUITER_ID)
        print("======================================\n")


if __name__ == "__main__":
    asyncio.run(main())