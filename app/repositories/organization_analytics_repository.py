from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.job import Job
from app.models.job_application import JobApplication
from app.models.interview import Interview


class OrganizationAnalyticsRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # 1. TOTAL USERS
    # ============================================================

    async def get_total_users(
        self,
        company_id: UUID,
    ) -> int:

        result = await self.db.execute(
            select(
                func.count(User.id)
            )
            .where(
                User.company_id == company_id
            )
        )

        return result.scalar() or 0

    # ============================================================
    # 2. ACTIVE USERS
    # ============================================================

    async def get_active_users(
        self,
        company_id: UUID,
    ) -> int:

        result = await self.db.execute(
            select(
                func.count(User.id)
            )
            .where(
                User.company_id == company_id,
                User.is_active.is_(True),
            )
        )

        return result.scalar() or 0

    # ============================================================
    # 3. TOTAL JOBS
    # ============================================================

    async def get_total_jobs(
        self,
        company_id: UUID,
    ) -> int:

        result = await self.db.execute(
            select(
                func.count(Job.id)
            )
            .where(
                Job.company_id == company_id
            )
        )

        return result.scalar() or 0

    # ============================================================
    # 4. ACTIVE JOBS
    # ============================================================

    async def get_active_jobs(
        self,
        company_id: UUID,
    ) -> int:

        result = await self.db.execute(
            select(
                func.count(Job.id)
            )
            .where(
                Job.company_id == company_id,
                Job.status == "active",
            )
        )

        return result.scalar() or 0

    # ============================================================
    # 5. TOTAL APPLICATIONS
    # ============================================================

    async def get_total_applications(
        self,
        company_id: UUID,
    ) -> int:

        result = await self.db.execute(
            select(
                func.count(JobApplication.id)
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id
            )
        )

        return result.scalar() or 0

    # ============================================================
    # 6. APPLICATIONS BY STATUS
    # ============================================================

    async def get_applications_by_status(
        self,
        company_id: UUID,
    ) -> list[tuple[str, int]]:

        result = await self.db.execute(
            select(
                JobApplication.status,
                func.count(
                    JobApplication.id
                ).label("count"),
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id
            )
            .group_by(
                JobApplication.status
            )
            .order_by(
                JobApplication.status
            )
        )

        return list(result.all())

    # ============================================================
    # 7. TOTAL INTERVIEWS
    # ============================================================

    async def get_total_interviews(
        self,
        company_id: UUID,
    ) -> int:

        result = await self.db.execute(
            select(
                func.count(Interview.id)
            )
            .where(
                Interview.company_id == company_id
            )
        )

        return result.scalar() or 0

    # ============================================================
    # 8. INTERVIEWS BY STATUS
    # ============================================================

    async def get_interviews_by_status(
        self,
        company_id: UUID,
    ) -> list[tuple[str, int]]:

        result = await self.db.execute(
            select(
                Interview.status,
                func.count(
                    Interview.id
                ).label("count"),
            )
            .where(
                Interview.company_id == company_id
            )
            .group_by(
                Interview.status
            )
            .order_by(
                Interview.status
            )
        )

        return list(result.all())

    # ============================================================
    # 9. APPLICATION TREND
    # ============================================================

    async def get_application_trend(
        self,
        company_id: UUID,
    ):

        result = await self.db.execute(
            select(
                func.date(
                    JobApplication.created_at
                ).label("date"),
                func.count(
                    JobApplication.id
                ).label("count"),
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id
            )
            .group_by(
                func.date(
                    JobApplication.created_at
                )
            )
            .order_by(
                func.date(
                    JobApplication.created_at
                )
            )
        )

        return [
            {
                "date": row.date,
                "count": row.count,
            }
            for row in result.all()
        ]

    # ============================================================
    # 10. RECRUITMENT FUNNEL
    # ============================================================

    async def get_recruitment_funnel(
        self,
        company_id: UUID,
    ):

        # --------------------------------------------------------
        # STATUS COUNTS
        # --------------------------------------------------------

        result = await self.db.execute(
            select(
                JobApplication.status,
                func.count(
                    JobApplication.id
                ).label("count"),
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id
            )
            .group_by(
                JobApplication.status
            )
        )

        status_counts = {
            row.status: int(row.count or 0)
            for row in result.all()
        }

        # --------------------------------------------------------
        # TOTAL APPLICATIONS
        # --------------------------------------------------------

        applications = sum(
            status_counts.values()
        )

        # --------------------------------------------------------
        # MATCHED
        #
        # Match score >= 70
        # --------------------------------------------------------

        matched_result = await self.db.execute(
            select(
                func.count(
                    JobApplication.id
                )
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id,
                JobApplication.match_score >= 70,
            )
        )

        matched = int(
            matched_result.scalar() or 0
        )

        # --------------------------------------------------------
        # SCREENED
        #
        # If an application has moved beyond the initial stage,
        # it has been screened.
        # --------------------------------------------------------

        screened = (
            status_counts.get("screened", 0)
            + status_counts.get("shortlisted", 0)
            + status_counts.get("interviewed", 0)
            + status_counts.get("interview", 0)
            + status_counts.get("finalist", 0)
            + status_counts.get("finalists", 0)
            + status_counts.get("selected", 0)
            + status_counts.get("hired", 0)
            + status_counts.get("rejected", 0)
        )

        # If there is no explicit pipeline status,
        # existing applications are considered screened.
        if screened == 0 and applications > 0:
            screened = applications

        # --------------------------------------------------------
        # SHORTLISTED
        # --------------------------------------------------------

        shortlisted = (
            status_counts.get("shortlisted", 0)
        )

        # --------------------------------------------------------
        # INTERVIEWED
        # --------------------------------------------------------

        interviewed = (
            status_counts.get("interviewed", 0)
            + status_counts.get("interview", 0)
        )

        # --------------------------------------------------------
        # FINALISTS
        # --------------------------------------------------------

        finalists = (
            status_counts.get("finalist", 0)
            + status_counts.get("finalists", 0)
        )

        # --------------------------------------------------------
        # SELECTED
        # --------------------------------------------------------

        selected = (
            status_counts.get("selected", 0)
            + status_counts.get("hired", 0)
        )

        # --------------------------------------------------------
        # REJECTED
        # --------------------------------------------------------

        rejected = (
            status_counts.get("rejected", 0)
        )

        # --------------------------------------------------------
        # ALWAYS RETURN ALL FIELDS
        # --------------------------------------------------------

        return {
            "company_id": company_id,
            "applications": applications,
            "matched": matched,
            "screened": screened,
            "shortlisted": shortlisted,
            "interviewed": interviewed,
            "finalists": finalists,
            "selected": selected,
            "rejected": rejected,
        }

    # ============================================================
    # 11. JOB-WISE RECRUITMENT ANALYTICS
    # ============================================================

    async def get_job_wise_recruitment_analytics(
        self,
        company_id: UUID,
    ):

        result = await self.db.execute(
            select(
                Job.id.label("job_id"),
                Job.title.label("job_title"),
                func.count(
                    JobApplication.id
                ).label("total_applications"),
            )
            .outerjoin(
                JobApplication,
                JobApplication.job_id == Job.id,
            )
            .where(
                Job.company_id == company_id
            )
            .group_by(
                Job.id,
                Job.title,
            )
            .order_by(
                func.count(
                    JobApplication.id
                ).desc()
            )
        )

        return {
            "company_id": company_id,
            "jobs": [
                {
                    "job_id": row.job_id,
                    "job_title": row.job_title,
                    "total_applications": int(
                        row.total_applications or 0
                    ),
                }
                for row in result.all()
            ],
        }

    # ============================================================
    # 12. HIRING RATE
    # ============================================================

    async def get_hiring_rate(
        self,
        company_id: UUID,
    ):

        total_result = await self.db.execute(
            select(
                func.count(
                    JobApplication.id
                )
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id
            )
        )

        total_applications = int(
            total_result.scalar() or 0
        )

        hired_result = await self.db.execute(
            select(
                func.count(
                    JobApplication.id
                )
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id,
                JobApplication.status.in_(
                    [
                        "selected",
                        "hired",
                    ]
                ),
            )
        )

        hired_applications = int(
            hired_result.scalar() or 0
        )

        hiring_rate = (
            hired_applications
            / total_applications
            * 100
            if total_applications > 0
            else 0
        )

        return {
            "company_id": company_id,
            "total_applications": total_applications,
            "hired_applications": hired_applications,
            "hiring_rate": round(
                hiring_rate,
                2,
            ),
        }

    # ============================================================
    # 13. AVERAGE TIME TO HIRE
    # ============================================================

    async def get_average_time_to_hire(
        self,
        company_id: UUID,
    ):

        result = await self.db.execute(
            select(
                func.avg(
                    func.extract(
                        "epoch",
                        JobApplication.selected_at
                        - JobApplication.created_at,
                    )
                )
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id,
                JobApplication.status.in_(
                    [
                        "selected",
                        "hired",
                    ]
                ),
                JobApplication.selected_at.is_not(
                    None
                ),
            )
        )

        average_seconds = result.scalar()

        if average_seconds is None:
            return {
                "average_time_to_hire_days": 0
            }

        average_days = (
            float(average_seconds)
            / 86400
        )

        return {
            "average_time_to_hire_days": round(
                average_days,
                2,
            )
        }

    # ============================================================
    # 14. OVERVIEW
    # ============================================================

    async def get_overview(
        self,
        company_id: UUID,
    ):

        # --------------------------------------------------------
        # TOTAL JOBS
        # --------------------------------------------------------

        total_jobs_result = await self.db.execute(
            select(
                func.count(Job.id)
            )
            .where(
                Job.company_id == company_id
            )
        )

        total_jobs = int(
            total_jobs_result.scalar() or 0
        )

        # --------------------------------------------------------
        # ACTIVE JOBS
        # --------------------------------------------------------

        active_jobs_result = await self.db.execute(
            select(
                func.count(Job.id)
            )
            .where(
                Job.company_id == company_id,
                Job.status == "active",
            )
        )

        active_jobs = int(
            active_jobs_result.scalar() or 0
        )

        # --------------------------------------------------------
        # APPLICATION STATUS
        # --------------------------------------------------------

        status_result = await self.db.execute(
            select(
                JobApplication.status,
                func.count(
                    JobApplication.id
                ).label("count"),
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id
            )
            .group_by(
                JobApplication.status
            )
        )

        status_counts = {
            row.status: int(row.count or 0)
            for row in status_result.all()
        }

        # --------------------------------------------------------
        # APPLICATIONS
        # --------------------------------------------------------

        applications = sum(
            status_counts.values()
        )

        # --------------------------------------------------------
        # MATCHED
        # --------------------------------------------------------

        matched_result = await self.db.execute(
            select(
                func.count(
                    JobApplication.id
                )
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id,
                JobApplication.match_score >= 70,
            )
        )

        matched = int(
            matched_result.scalar() or 0
        )

        # --------------------------------------------------------
        # SHORTLISTED
        # --------------------------------------------------------

        shortlisted = status_counts.get(
            "shortlisted",
            0,
        )

        # --------------------------------------------------------
        # INTERVIEWS
        # --------------------------------------------------------

        interviews = (
            status_counts.get(
                "interviewed",
                0,
            )
            + status_counts.get(
                "interview",
                0,
            )
        )

        # --------------------------------------------------------
        # FINALISTS
        # --------------------------------------------------------

        finalists = (
            status_counts.get(
                "finalist",
                0,
            )
            + status_counts.get(
                "finalists",
                0,
            )
        )

        # --------------------------------------------------------
        # SELECTED
        # --------------------------------------------------------

        selected = (
            status_counts.get(
                "selected",
                0,
            )
            + status_counts.get(
                "hired",
                0,
            )
        )

        # --------------------------------------------------------
        # REJECTED
        # --------------------------------------------------------

        rejected = status_counts.get(
            "rejected",
            0,
        )

        # --------------------------------------------------------
        # CONVERSION
        # --------------------------------------------------------

        conversion = (
            selected
            / applications
            * 100
            if applications > 0
            else 0
        )

        # --------------------------------------------------------
        # AVERAGE ATS
        # --------------------------------------------------------

        ats_result = await self.db.execute(
            select(
                func.avg(
                    JobApplication.ats_score
                )
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id
            )
        )

        avg_ats = float(
            ats_result.scalar() or 0
        )

        # --------------------------------------------------------
        # TIME TO HIRE
        # --------------------------------------------------------

        time_result = await self.db.execute(
            select(
                func.avg(
                    func.extract(
                        "epoch",
                        JobApplication.selected_at
                        - JobApplication.created_at,
                    )
                )
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id,
                JobApplication.status.in_(
                    [
                        "selected",
                        "hired",
                    ]
                ),
                JobApplication.selected_at.is_not(
                    None
                ),
            )
        )

        average_seconds = time_result.scalar()

        if average_seconds is None:
            time_to_hire = 0
        else:
            time_to_hire = (
                float(average_seconds)
                / 86400
            )

        return {
            "company_id": company_id,
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "applications": applications,
            "matched": matched,
            "shortlisted": shortlisted,
            "interviews": interviews,
            "finalists": finalists,
            "selected": selected,
            "rejected": rejected,
            "conversion": round(
                conversion,
                2,
            ),
            "avg_ats": round(
                avg_ats,
                2,
            ),
            "time_to_hire": round(
                time_to_hire,
                2,
            ),
        }

    # ============================================================
    # 15. JOB PERFORMANCE
    # ============================================================

    async def get_job_performance(
        self,
        company_id: UUID,
    ):

        result = await self.db.execute(
            select(
                Job.id,
                Job.title,
                Job.department,
                Job.opened_at,
            )
            .where(
                Job.company_id == company_id
            )
            .order_by(
                Job.opened_at.desc()
            )
        )

        rows = result.all()

        jobs = []

        now = datetime.now(timezone.utc)

        for row in rows:

            job_id = row.id

            # ----------------------------------------------------
            # APPLICATIONS
            # ----------------------------------------------------

            applications_result = await self.db.execute(
                select(
                    func.count(
                        JobApplication.id
                    )
                )
                .where(
                    JobApplication.job_id == job_id
                )
            )

            applications = int(
                applications_result.scalar() or 0
            )

            # ----------------------------------------------------
            # MATCHED
            # ----------------------------------------------------

            matched_result = await self.db.execute(
                select(
                    func.count(
                        JobApplication.id
                    )
                )
                .where(
                    JobApplication.job_id == job_id,
                    JobApplication.match_score >= 70,
                )
            )

            matched = int(
                matched_result.scalar() or 0
            )

            # ----------------------------------------------------
            # SHORTLISTED
            # ----------------------------------------------------

            shortlisted_result = await self.db.execute(
                select(
                    func.count(
                        JobApplication.id
                    )
                )
                .where(
                    JobApplication.job_id == job_id,
                    JobApplication.status == "shortlisted",
                )
            )

            shortlisted = int(
                shortlisted_result.scalar() or 0
            )

            # ----------------------------------------------------
            # INTERVIEWS
            # ----------------------------------------------------

            interviews_result = await self.db.execute(
                select(
                    func.count(
                        JobApplication.id
                    )
                )
                .where(
                    JobApplication.job_id == job_id,
                    JobApplication.status.in_(
                        [
                            "interviewed",
                            "interview",
                        ]
                    ),
                )
            )

            interviews = int(
                interviews_result.scalar() or 0
            )

            # ----------------------------------------------------
            # SELECTED
            # ----------------------------------------------------

            selected_result = await self.db.execute(
                select(
                    func.count(
                        JobApplication.id
                    )
                )
                .where(
                    JobApplication.job_id == job_id,
                    JobApplication.status.in_(
                        [
                            "selected",
                            "hired",
                        ]
                    ),
                )
            )

            selected = int(
                selected_result.scalar() or 0
            )

            # ----------------------------------------------------
            # AVERAGE ATS
            # ----------------------------------------------------

            ats_result = await self.db.execute(
                select(
                    func.avg(
                        JobApplication.ats_score
                    )
                )
                .where(
                    JobApplication.job_id == job_id
                )
            )

            avg_ats = float(
                ats_result.scalar() or 0
            )

            # ----------------------------------------------------
            # DAYS OPEN
            # ----------------------------------------------------

            if row.opened_at:

                opened_at = row.opened_at

                if opened_at.tzinfo is None:
                    opened_at = opened_at.replace(
                        tzinfo=timezone.utc
                    )

                days_open = max(
                    0,
                    (
                        now - opened_at
                    ).days,
                )

            else:

                days_open = 0

            # ----------------------------------------------------
            # MATCH RATE
            # ----------------------------------------------------

            match_rate = (
                matched
                / applications
                * 100
                if applications > 0
                else 0
            )

            # ----------------------------------------------------
            # CONVERSION
            # ----------------------------------------------------

            conversion = (
                selected
                / applications
                * 100
                if applications > 0
                else 0
            )

            jobs.append(
                {
                    "job_id": job_id,
                    "job_title": row.title,
                    "department": row.department,
                    "applications": applications,
                    "matched": matched,
                    "match_rate": round(
                        match_rate,
                        1,
                    ),
                    "shortlisted": shortlisted,
                    "interviews": interviews,
                    "selected": selected,
                    "avg_ats": round(
                        avg_ats,
                        1,
                    ),
                    "days_open": days_open,
                    "conversion": round(
                        conversion,
                        1,
                    ),
                }
            )

        return {
            "company_id": company_id,
            "jobs": jobs,
        }

    # ============================================================
    # 16. CANDIDATE QUALITY
    # ============================================================

    async def get_candidate_quality(
        self,
        company_id: UUID,
    ):

        result = await self.db.execute(
            select(
                JobApplication.ats_score,
                JobApplication.match_score,
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id
            )
        )

        rows = result.all()

        total_candidates = len(rows)

        ats_scores = [
            float(row.ats_score)
            for row in rows
            if row.ats_score is not None
        ]

        match_scores = [
            float(row.match_score)
            for row in rows
            if row.match_score is not None
        ]

        average_ats_score = (
            sum(ats_scores)
            / len(ats_scores)
            if ats_scores
            else 0.0
        )

        average_match_score = (
            sum(match_scores)
            / len(match_scores)
            if match_scores
            else 0.0
        )

        # --------------------------------------------------------
        # SCORE DISTRIBUTION
        # Based on ATS score
        # --------------------------------------------------------

        score_90_100 = 0
        score_80_89 = 0
        score_70_79 = 0
        score_60_69 = 0
        below_60 = 0

        for score in ats_scores:

            if score >= 90:
                score_90_100 += 1

            elif score >= 80:
                score_80_89 += 1

            elif score >= 70:
                score_70_79 += 1

            elif score >= 60:
                score_60_69 += 1

            else:
                below_60 += 1

        return {
            "company_id": company_id,
            "total_candidates": total_candidates,
            "average_ats_score": round(
                average_ats_score,
                1,
            ),
            "average_match_score": round(
                average_match_score,
                1,
            ),
            "score_distribution": {
                "score_90_100": score_90_100,
                "score_80_89": score_80_89,
                "score_70_79": score_70_79,
                "score_60_69": score_60_69,
                "below_60": below_60,
            },
            "above_90": score_90_100,
            "below_60": below_60,
        }

    # ============================================================
    # 17. SOURCE ANALYTICS
    # ============================================================

    async def get_source_analytics(
        self,
        company_id: UUID,
    ):

        result = await self.db.execute(
            select(
                JobApplication.source,
                func.count(
                    JobApplication.id
                ).label("applications"),
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id
            )
            .group_by(
                JobApplication.source
            )
            .order_by(
                func.count(
                    JobApplication.id
                ).desc()
            )
        )

        sources = []

        for row in result.all():

            source = (
                row.source
                or "Unknown"
            )

            applications = int(
                row.applications or 0
            )

            # ----------------------------------------------------
            # SHORTLISTED
            # ----------------------------------------------------

            shortlisted_result = await self.db.execute(
                select(
                    func.count(
                        JobApplication.id
                    )
                )
                .join(
                    Job,
                    Job.id == JobApplication.job_id,
                )
                .where(
                    Job.company_id == company_id,
                    JobApplication.status
                    == "shortlisted",
                    JobApplication.source
                    == row.source,
                )
            )

            shortlisted = int(
                shortlisted_result.scalar() or 0
            )

            # ----------------------------------------------------
            # INTERVIEWS
            # ----------------------------------------------------

            interviews_result = await self.db.execute(
                select(
                    func.count(
                        JobApplication.id
                    )
                )
                .join(
                    Job,
                    Job.id == JobApplication.job_id,
                )
                .where(
                    Job.company_id == company_id,
                    JobApplication.status.in_(
                        [
                            "interviewed",
                            "interview",
                        ]
                    ),
                    JobApplication.source
                    == row.source,
                )
            )

            interviews = int(
                interviews_result.scalar() or 0
            )

            # ----------------------------------------------------
            # HIRES
            # ----------------------------------------------------

            hires_result = await self.db.execute(
                select(
                    func.count(
                        JobApplication.id
                    )
                )
                .join(
                    Job,
                    Job.id == JobApplication.job_id,
                )
                .where(
                    Job.company_id == company_id,
                    JobApplication.source
                    == row.source,
                    JobApplication.status.in_(
                        [
                            "selected",
                            "hired",
                        ]
                    ),
                )
            )

            hires = int(
                hires_result.scalar() or 0
            )

            # ----------------------------------------------------
            # CONVERSION
            # ----------------------------------------------------

            conversion = (
                hires
                / applications
                * 100
                if applications > 0
                else 0.0
            )

            sources.append(
                {
                    "source": source,
                    "applications": applications,
                    "shortlisted": shortlisted,
                    "interviews": interviews,
                    "hires": hires,
                    "conversion": round(
                        conversion,
                        2,
                    ),
                }
            )

        return {
            "company_id": company_id,
            "sources": sources,
        }

    # ============================================================
    # 18. TIME TO HIRE
    # ============================================================

    async def get_time_to_hire(
        self,
        company_id: UUID,
    ):

        # --------------------------------------------------------
        # JOB-LEVEL TIME TO HIRE
        # --------------------------------------------------------

        result = await self.db.execute(
            select(
                Job.id,
                Job.title,

                func.avg(
                    func.extract(
                        "epoch",
                        JobApplication.selected_at
                        - JobApplication.created_at,
                    )
                ).label(
                    "average_seconds"
                ),

                func.count(
                    JobApplication.id
                ).label("hires"),
            )
            .join(
                JobApplication,
                JobApplication.job_id == Job.id,
            )
            .where(
                Job.company_id == company_id,
                JobApplication.status.in_(
                    [
                        "selected",
                        "hired",
                    ]
                ),
                JobApplication.selected_at.is_not(
                    None
                ),
            )
            .group_by(
                Job.id,
                Job.title,
            )
        )

        jobs = []
        values = []

        for row in result.all():

            days = (
                float(
                    row.average_seconds or 0
                )
                / 86400
            )

            values.append(days)

            jobs.append(
                {
                    "job_id": row.id,
                    "job_title": row.title,
                    "average_days": round(
                        days,
                        2,
                    ),
                    "hires": int(
                        row.hires or 0
                    ),
                }
            )

        # --------------------------------------------------------
        # OVERALL TIME TO HIRE
        # --------------------------------------------------------

        average_time_to_hire = (
            sum(values)
            / len(values)
            if values
            else 0
        )

        
        # --------------------------------------------------------
        # STAGE TIMINGS
        #
        # Your current database only has:
        #
        # created_at
        # selected_at
        #
        # It does not expose separate timestamps for:
        #
        # screening
        # shortlist
        # interview
        #
        # Therefore we DO NOT invent those values.
        #
        # They remain 0 until those timestamps exist.
        # --------------------------------------------------------

        job_to_first_application = 0.0
        application_to_screening = 0.0
        screening_to_shortlist = 0.0
        shortlist_to_interview = 0.0
        interview_to_selection = (
            round(
                average_time_to_hire,
                2,
            )
            if average_time_to_hire > 0
            else 0.0
        )

        return {
            "company_id": company_id,

            "average_time_to_hire": round(
                average_time_to_hire,
                2,
            ),

           

            "jobs": jobs,

            "job_to_first_application":
                job_to_first_application,

            "application_to_screening":
                application_to_screening,

            "screening_to_shortlist":
                screening_to_shortlist,

            "shortlist_to_interview":
                shortlist_to_interview,

            "interview_to_selection":
                interview_to_selection,
        }

    # ============================================================
    # 19. RECRUITER ANALYTICS
    # ============================================================

        # ============================================================
    # 19. RECRUITER ANALYTICS
    # ============================================================

    async def get_recruiter_analytics(
        self,
        company_id: UUID,
    ):

        # --------------------------------------------------------
        # GET RECRUITERS FROM JOBS
        #
        # Job.recruiter_id is the recruiter assigned to the job.
        # --------------------------------------------------------

        recruiter_result = await self.db.execute(
            select(
                User.id,
                User.name,
                func.count(
                    func.distinct(Job.id)
                ).label("jobs"),
            )
            .join(
                Job,
                Job.recruiter_id == User.id,
            )
            .where(
                Job.company_id == company_id,
                Job.recruiter_id.is_not(None),
            )
            .group_by(
                User.id,
                User.name,
            )
            .order_by(
                func.count(
                    func.distinct(Job.id)
                ).desc()
            )
        )

        recruiters = []

        # --------------------------------------------------------
        # PROCESS EACH RECRUITER
        # --------------------------------------------------------

        for recruiter in recruiter_result.all():

            recruiter_id = recruiter.id

            jobs = int(
                recruiter.jobs or 0
            )

            # ----------------------------------------------------
            # APPLICATIONS
            # ----------------------------------------------------

            applications_result = await self.db.execute(
                select(
                    func.count(
                        JobApplication.id
                    )
                )
                .join(
                    Job,
                    Job.id == JobApplication.job_id,
                )
                .where(
                    Job.company_id == company_id,
                    Job.recruiter_id == recruiter_id,
                )
            )

            applications = int(
                applications_result.scalar() or 0
            )

            # ----------------------------------------------------
            # SHORTLISTED
            # ----------------------------------------------------

            shortlisted_result = await self.db.execute(
                select(
                    func.count(
                        JobApplication.id
                    )
                )
                .join(
                    Job,
                    Job.id == JobApplication.job_id,
                )
                .where(
                    Job.company_id == company_id,
                    Job.recruiter_id == recruiter_id,
                    JobApplication.status == "shortlisted",
                )
            )

            shortlisted = int(
                shortlisted_result.scalar() or 0
            )

            # ----------------------------------------------------
            # INTERVIEWS
            # ----------------------------------------------------

            interviews_result = await self.db.execute(
                select(
                    func.count(
                        JobApplication.id
                    )
                )
                .join(
                    Job,
                    Job.id == JobApplication.job_id,
                )
                .where(
                    Job.company_id == company_id,
                    Job.recruiter_id == recruiter_id,
                    JobApplication.status.in_(
                        [
                            "interview",
                            "interviewed",
                        ]
                    ),
                )
            )

            interviews = int(
                interviews_result.scalar() or 0
            )

            # ----------------------------------------------------
            # SELECTED / HIRED
            # ----------------------------------------------------

            selected_result = await self.db.execute(
                select(
                    func.count(
                        JobApplication.id
                    )
                )
                .join(
                    Job,
                    Job.id == JobApplication.job_id,
                )
                .where(
                    Job.company_id == company_id,
                    Job.recruiter_id == recruiter_id,
                    JobApplication.status.in_(
                        [
                            "selected",
                            "hired",
                        ]
                    ),
                )
            )

            selected = int(
                selected_result.scalar() or 0
            )

            # ----------------------------------------------------
            # AVERAGE TIME TO HIRE
            # ----------------------------------------------------

            time_result = await self.db.execute(
                select(
                    func.avg(
                        func.extract(
                            "epoch",
                            JobApplication.selected_at
                            - JobApplication.created_at,
                        )
                    )
                )
                .join(
                    Job,
                    Job.id == JobApplication.job_id,
                )
                .where(
                    Job.company_id == company_id,
                    Job.recruiter_id == recruiter_id,
                    JobApplication.status.in_(
                        [
                            "selected",
                            "hired",
                        ]
                    ),
                    JobApplication.selected_at.is_not(None),
                )
            )

            average_seconds = time_result.scalar()

            average_days = (
                float(average_seconds) / 86400
                if average_seconds is not None
                else 0.0
            )

            # ----------------------------------------------------
            # CONVERSION
            # ----------------------------------------------------

            conversion = (
                selected / applications * 100
                if applications > 0
                else 0.0
            )

            # ----------------------------------------------------
            # ADD RECRUITER
            # ----------------------------------------------------

            recruiters.append(
                {
                    "recruiter_id": recruiter_id,

                    "recruiter_name": (
                        recruiter.name or "Unknown"
                    ),

                    "jobs": jobs,

                    "applications": applications,

                    "shortlisted": shortlisted,

                    "interviews": interviews,

                    "selected": selected,

                    "avg_days": round(
                        average_days,
                        2,
                    ),

                    "conversion": round(
                        conversion,
                        2,
                    ),
                }
            )

        # --------------------------------------------------------
        # FINAL RESPONSE
        # --------------------------------------------------------

        return {
            "company_id": company_id,
            "recruiters": recruiters,
        }


    # ============================================================
    # 20. SKILL GAP
    # ============================================================

    async def get_skill_gap(
        self,
        company_id: UUID,
    ):

        result = await self.db.execute(
            select(
                Job.required_skills
            )
            .where(
                Job.company_id == company_id
            )
        )

        required = {}

        for row in result.all():

            for skill in (
                row.required_skills or []
            ):

                if not isinstance(
                    skill,
                    str,
                ):
                    continue

                skill_name = (
                    skill.strip()
                    .lower()
                )

                if not skill_name:
                    continue

                required[skill_name] = (
                    required.get(
                        skill_name,
                        0,
                    )
                    + 1
                )

        # --------------------------------------------------------
        # MOST REQUESTED SKILLS
        # --------------------------------------------------------

        most_requested_skills = []

        for (
            skill,
            required_count,
        ) in required.items():

            most_requested_skills.append(
                {
                    "skill": skill,
                    "count": required_count,
                }
            )

        most_requested_skills.sort(
            key=lambda x: x["count"],
            reverse=True,
        )

        # --------------------------------------------------------
        # CANDIDATE GAPS
        # --------------------------------------------------------

        candidate_gaps = []

        for (
            skill,
            required_count,
        ) in required.items():

            candidate_gaps.append(
                {
                    "skill": skill,
                    "count": required_count,
                }
            )

        candidate_gaps.sort(
            key=lambda x: x["count"],
            reverse=True,
        )

        # --------------------------------------------------------
        # LIMIT RESULTS
        # --------------------------------------------------------

        most_requested_skills = (
            most_requested_skills[:10]
        )

        candidate_gaps = (
            candidate_gaps[:10]
        )

        # --------------------------------------------------------
        # FINAL RESPONSE
        # --------------------------------------------------------

        return {
            "company_id": company_id,
            "most_requested_skills":
                most_requested_skills,
            "candidate_gaps":
                candidate_gaps,
        }
    # ============================================================
    # 21. JOB HEALTH
    # ============================================================

    async def get_job_health(
        self,
        company_id: UUID,
    ):

        stmt = (
            select(
                Job.id.label(
                    "job_id"
                ),

                Job.title.label(
                    "job_title"
                ),

                Job.status.label(
                    "status"
                ),

                Job.opened_at.label(
                    "opened_at"
                ),

                func.count(
                    JobApplication.id
                ).label(
                    "applications"
                ),

                func.count(
                    case(
                        (
                            JobApplication.match_score
                            >= 70,
                            1,
                        )
                    )
                ).label(
                    "qualified_matches"
                ),

                func.coalesce(
                    func.avg(
                        JobApplication.match_score
                    ),
                    0,
                ).label(
                    "average_score"
                ),
            )
            .outerjoin(
                JobApplication,
                JobApplication.job_id
                == Job.id,
            )
            .where(
                Job.company_id == company_id
            )
            .group_by(
                Job.id,
                Job.title,
                Job.status,
                Job.opened_at,
            )
            .order_by(
                Job.opened_at.desc()
            )
        )

        result = await self.db.execute(
            stmt
        )

        rows = result.all()

        now = datetime.now(
            timezone.utc
        )

        job_health = []

        for row in rows:

            # ----------------------------------------------------
            # DAYS OPEN
            # ----------------------------------------------------

            if row.opened_at:

                opened_at = row.opened_at

                if (
                    opened_at.tzinfo
                    is None
                ):
                    opened_at = (
                        opened_at.replace(
                            tzinfo=timezone.utc
                        )
                    )

                days_open = max(
                    0,
                    (
                        now - opened_at
                    ).days,
                )

            else:

                days_open = 0

            # ----------------------------------------------------
            # VALUES
            # ----------------------------------------------------

            applications = int(
                row.applications or 0
            )

            qualified_matches = int(
                row.qualified_matches or 0
            )

            average_score = round(
                float(
                    row.average_score or 0
                ),
                1,
            )

            # ----------------------------------------------------
            # HEALTH STATUS
            # ----------------------------------------------------

            if row.status in (
                "closed",
                "cancelled",
            ):

                health_status = "Closed"

            elif (
                days_open >= 45
                and (
                    applications < 10
                    or average_score < 50
                )
            ):

                health_status = "At Risk"

            elif (
                applications < 5
                or average_score < 60
            ):

                health_status = (
                    "Needs Attention"
                )

            else:

                health_status = "Healthy"

            job_health.append(
                {
                    "job_id":
                        row.job_id,

                    "job_title":
                        row.job_title,

                    "status":
                        row.status,

                    "applications":
                        applications,

                    "qualified_matches":
                        qualified_matches,

                    "average_score":
                        average_score,

                    "days_open":
                        days_open,

                    "health_status":
                        health_status,
                }
            )

        return job_health

    # ============================================================
    # 22. COMPLETE RECRUITMENT DASHBOARD
    # ============================================================

    async def get_recruitment_dashboard(
        self,
        company_id: UUID,
    ):

        # --------------------------------------------------------
        # OVERVIEW
        # --------------------------------------------------------

        overview = await (
            self.get_overview(
                company_id
            )
        )

        # --------------------------------------------------------
        # JOB PERFORMANCE
        # --------------------------------------------------------

        job_performance = await (
            self.get_job_performance(
                company_id
            )
        )

        # --------------------------------------------------------
        # FUNNEL
        # --------------------------------------------------------

        funnel = await (
            self.get_recruitment_funnel(
                company_id
            )
        )

        # --------------------------------------------------------
        # CANDIDATE QUALITY
        # --------------------------------------------------------

        candidate_quality = await (
            self.get_candidate_quality(
                company_id
            )
        )

        # --------------------------------------------------------
        # SOURCES
        # --------------------------------------------------------

        sources = await (
            self.get_source_analytics(
                company_id
            )
        )

        # --------------------------------------------------------
        # TIME TO HIRE
        # --------------------------------------------------------

        time_to_hire = await (
            self.get_time_to_hire(
                company_id
            )
        )

        # --------------------------------------------------------
        # RECRUITERS
        # --------------------------------------------------------

        recruiters = await (
            self.get_recruiter_analytics(
                company_id
            )
        )

        # --------------------------------------------------------
        # SKILL GAP
        # --------------------------------------------------------

        skill_gap = await (
            self.get_skill_gap(
                company_id
            )
        )

        # --------------------------------------------------------
        # JOB HEALTH
        # --------------------------------------------------------

        job_health = await (
            self.get_job_health(
                company_id
            )
        )

        # --------------------------------------------------------
        # FINAL RESPONSE
        # --------------------------------------------------------

        return {
            "company_id":
                company_id,

            "overview":
                overview,

            "job_performance":
                job_performance,

            "funnel":
                funnel,

            "candidate_quality":
                candidate_quality,

            "sources":
                sources,

            "time_to_hire":
                time_to_hire,

            "recruiters":
                recruiters,

            "skill_gap":
                skill_gap,

            "job_health":
                job_health,
        }