
import re
from typing import Any


class JobMatchingService:
    """Calculate candidate skill, experience, education, ATS and job-match scores."""

    @staticmethod
    def normalize(value: str | None) -> str:
        if not value:
            return ""

        value = value.lower().strip()
        value = re.sub(r"[^a-z0-9+#.\s]", " ", value)
        value = re.sub(r"\s+", " ", value)

        return value

    @classmethod
    def calculate_skill_score(
        cls,
        candidate_skills: list[str],
        required_skills: list[str],
        preferred_skills: list[str],
    ) -> float:
        candidate = {
            cls.normalize(skill)
            for skill in candidate_skills
            if skill
        }

        required = {
            cls.normalize(skill)
            for skill in required_skills
            if skill
        }

        preferred = {
            cls.normalize(skill)
            for skill in preferred_skills
            if skill
        }

        if not required and not preferred:
            return 100.0

        required_score = 0.0
        if required:
            matched_required = candidate.intersection(required)
            required_score = (
                len(matched_required) / len(required)
            ) * 80

        preferred_score = 0.0
        if preferred:
            matched_preferred = candidate.intersection(preferred)
            preferred_score = (
                len(matched_preferred) / len(preferred)
            ) * 20

        return round(min(required_score + preferred_score, 100), 2)

    @classmethod
    def extract_years(cls, experience: str | None) -> float:
        if not experience:
            return 0.0

        text = cls.normalize(experience)
        match = re.search(r"(\d+(?:\.\d+)?)", text)

        if not match:
            return 0.0

        return float(match.group(1))

    @classmethod
    def calculate_experience_score(
        cls,
        candidate_experience: str | None,
        min_experience: int | None,
        max_experience: int | None,
    ) -> float:
        candidate_years = cls.extract_years(candidate_experience)

        if min_experience is None and max_experience is None:
            return 100.0

        if min_experience is not None and candidate_years < min_experience:
            if min_experience <= 0:
                return 100.0

            return round(
                (candidate_years / min_experience) * 100,
                2,
            )

        # Candidates meeting the minimum receive full credit.
        # Experience above the maximum is not penalized here.
        return 100.0

    @classmethod
    def calculate_education_score(
        cls,
        candidate_education: str | None,
        required_education: str | None,
    ) -> float:
        if not required_education:
            return 100.0

        if not candidate_education:
            return 0.0

        candidate_words = set(
            cls.normalize(candidate_education).split()
        )
        required_words = set(
            cls.normalize(required_education).split()
        )

        if not required_words:
            return 100.0

        if required_words.issubset(candidate_words):
            return 100.0

        matched = candidate_words.intersection(required_words)

        if not matched:
            return 0.0

        return round(
            (len(matched) / len(required_words)) * 100,
            2,
        )

    @classmethod
    def calculate_role_score(
        cls,
        job_title: str | None,
        career_goal: str | None,
        work_titles: list[str],
    ) -> float:
        if not job_title:
            return 100.0

        job_words = set(cls.normalize(job_title).split())

        if not job_words:
            return 100.0

        candidate_text = " ".join(
            [career_goal or "", *work_titles]
        )
        candidate_words = set(
            cls.normalize(candidate_text).split()
        )

        matched = job_words.intersection(candidate_words)

        return round(
            (len(matched) / len(job_words)) * 100,
            2,
        )

    @classmethod
    def _get_candidate_details(
        cls,
        profile: Any,
    ) -> tuple[list[str], list[str]]:
        candidate_skills = list(profile.skills or [])
        work_titles: list[str] = []

        for experience in (profile.work_experiences or []):
            if experience.job_title:
                work_titles.append(experience.job_title)

            if experience.skills:
                candidate_skills.extend(
                    skill.strip()
                    for skill in experience.skills.split(",")
                    if skill.strip()
                )

        return candidate_skills, work_titles

    @classmethod
    def calculate_ats_score(
        cls,
        *,
        job: Any,
        profile: Any,
        application_experience: str | None,
    ) -> float:
        config = job.ats_configuration or {}

        weights = {
            "skills": config.get("skills", 30),
            "experience": config.get("experience", 20),
            "education": config.get("education", 15),
            "role_relevance": config.get("role_relevance", 20),
        }

        candidate_skills, work_titles = cls._get_candidate_details(profile)

        skill_score = cls.calculate_skill_score(
            candidate_skills=candidate_skills,
            required_skills=job.required_skills or [],
            preferred_skills=job.preferred_skills or [],
        )

        experience_score = cls.calculate_experience_score(
            candidate_experience=application_experience,
            min_experience=job.min_experience,
            max_experience=job.max_experience,
        )

        education_score = cls.calculate_education_score(
            candidate_education=profile.education,
            required_education=job.education,
        )

        role_score = cls.calculate_role_score(
            job_title=job.title,
            career_goal=profile.career_goal,
            work_titles=work_titles,
        )

        applicable_weight = sum(weights.values())

        if applicable_weight <= 0:
            return 0.0

        weighted_score = (
            skill_score * weights["skills"]
            + experience_score * weights["experience"]
            + education_score * weights["education"]
            + role_score * weights["role_relevance"]
        )

        return round(weighted_score / applicable_weight, 2)

    @classmethod
    def calculate_match_score(
        cls,
        *,
        job: Any,
        profile: Any,
        application_experience: str | None,
    ) -> float:
        candidate_skills, work_titles = cls._get_candidate_details(profile)

        skill_score = cls.calculate_skill_score(
            candidate_skills=candidate_skills,
            required_skills=job.required_skills or [],
            preferred_skills=job.preferred_skills or [],
        )

        experience_score = cls.calculate_experience_score(
            candidate_experience=application_experience,
            min_experience=job.min_experience,
            max_experience=job.max_experience,
        )

        role_score = cls.calculate_role_score(
            job_title=job.title,
            career_goal=profile.career_goal,
            work_titles=work_titles,
        )

        education_score = cls.calculate_education_score(
            candidate_education=profile.education,
            required_education=job.education,
        )

        return round(
            skill_score * 0.40
            + experience_score * 0.25
            + role_score * 0.20
            + education_score * 0.15,
            2,
        )
