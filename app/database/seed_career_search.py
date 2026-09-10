import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal
from app.models.career_search_knowledge import (
    CareerSearchKnowledge,
)


CAREERS = [
    {
        "query": "doctor",
        "keywords": [
            "doctor",
            "become a doctor",
            "i want to become a doctor",
            "how to become a doctor",
            "medical doctor",
            "medicine",
            "mbbs",
            "medical career",
        ],
        "result": {
            "career": "Doctor",
            "career_persona": "Medical Career Path",
            "career_overview": (
                "A doctor diagnoses, treats, and helps "
                "prevent illnesses and supports patient health."
            ),
            "recommended_stream": "PCB with Biology",
            "target_exams": [
                "NEET-UG"
            ],
            "primary_skill": "Biology",
            "roadmap": [
                {
                    "step": 1,
                    "title": "Complete school education",
                    "description": (
                        "Build a strong foundation in "
                        "Physics, Chemistry and Biology."
                    ),
                },
                {
                    "step": 2,
                    "title": "Prepare for NEET-UG",
                    "description": (
                        "Prepare for the medical entrance "
                        "examination."
                    ),
                },
                {
                    "step": 3,
                    "title": "Complete MBBS",
                    "description": (
                        "Pursue an MBBS degree from "
                        "a recognized medical college."
                    ),
                },
                {
                    "step": 4,
                    "title": "Medical practice",
                    "description": (
                        "Complete internship and required "
                        "registration before practicing."
                    ),
                },
            ],
            "recommended_colleges": [],
        },
    },

    {
        "query": "software engineer",
        "keywords": [
            "software engineer",
            "software developer",
            "developer",
            "programmer",
            "coding career",
            "software development",
            "i want to become a software engineer",
            "i want to become a software developer",
        ],
        "result": {
            "career": "Software Engineer",
            "career_persona": "Software Engineering Career Path",
            "career_overview": (
                "A software engineer designs, develops, "
                "tests and maintains software applications."
            ),
            "recommended_stream": "Science / Computer Science",
            "target_exams": [],
            "primary_skill": "Programming",
            "roadmap": [
                {
                    "step": 1,
                    "title": "Learn programming",
                    "description": (
                        "Start with languages such as "
                        "Python, Java or C++."
                    ),
                },
                {
                    "step": 2,
                    "title": "Learn computer science",
                    "description": (
                        "Study data structures, algorithms "
                        "and databases."
                    ),
                },
                {
                    "step": 3,
                    "title": "Build projects",
                    "description": (
                        "Create real-world projects "
                        "to build practical experience."
                    ),
                },
                {
                    "step": 4,
                    "title": "Prepare for jobs",
                    "description": (
                        "Build a portfolio and prepare "
                        "for technical interviews."
                    ),
                },
            ],
            "recommended_colleges": [],
        },
    },

    {
        "query": "lawyer",
        "keywords": [
            "lawyer",
            "advocate",
            "law",
            "legal career",
            "become a lawyer",
            "i want to become a lawyer",
            "legal profession",
        ],
        "result": {
            "career": "Lawyer",
            "career_persona": "Legal Career Path",
            "career_overview": (
                "A lawyer provides legal advice, "
                "represents clients and works with legal matters."
            ),
            "recommended_stream": "Any stream",
            "target_exams": [
                "CLAT"
            ],
            "primary_skill": "Legal reasoning",
            "roadmap": [
                {
                    "step": 1,
                    "title": "Complete school education",
                    "description": (
                        "Develop communication, reading "
                        "and analytical skills."
                    ),
                },
                {
                    "step": 2,
                    "title": "Prepare for law entrance",
                    "description": (
                        "Prepare for relevant law entrance "
                        "examinations."
                    ),
                },
                {
                    "step": 3,
                    "title": "Complete law degree",
                    "description": (
                        "Pursue an undergraduate or "
                        "integrated law program."
                    ),
                },
                {
                    "step": 4,
                    "title": "Build legal experience",
                    "description": (
                        "Gain practical experience through "
                        "internships and legal work."
                    ),
                },
            ],
            "recommended_colleges": [],
        },
    },

    {
        "query": "chartered accountant",
        "keywords": [
            "chartered accountant",
            "ca",
            "become a ca",
            "accountant",
            "accounting career",
            "finance career",
            "i want to become a chartered accountant",
        ],
        "result": {
            "career": "Chartered Accountant",
            "career_persona": "Finance and Accounting Career Path",
            "career_overview": (
                "A chartered accountant works in accounting, "
                "auditing, taxation and financial management."
            ),
            "recommended_stream": "Commerce",
            "target_exams": [],
            "primary_skill": "Accounting",
            "roadmap": [
                {
                    "step": 1,
                    "title": "Build accounting foundation",
                    "description": (
                        "Develop strong fundamentals "
                        "in accounting and mathematics."
                    ),
                },
                {
                    "step": 2,
                    "title": "Start CA pathway",
                    "description": (
                        "Begin the appropriate CA "
                        "course and examination pathway."
                    ),
                },
                {
                    "step": 3,
                    "title": "Complete practical training",
                    "description": (
                        "Gain professional experience "
                        "through required training."
                    ),
                },
                {
                    "step": 4,
                    "title": "Qualify as CA",
                    "description": (
                        "Complete the required examinations "
                        "and professional requirements."
                    ),
                },
            ],
            "recommended_colleges": [],
        },
    },

    {
        "query": "pilot",
        "keywords": [
            "pilot",
            "airline pilot",
            "commercial pilot",
            "become a pilot",
            "i want to become a pilot",
            "aviation career",
        ],
        "result": {
            "career": "Pilot",
            "career_persona": "Aviation Career Path",
            "career_overview": (
                "A pilot operates aircraft and is responsible "
                "for safe flight operations."
            ),
            "recommended_stream": "Science with Physics and Mathematics",
            "target_exams": [],
            "primary_skill": "Aviation knowledge",
            "roadmap": [
                {
                    "step": 1,
                    "title": "Complete school education",
                    "description": (
                        "Build a strong foundation in "
                        "Physics and Mathematics."
                    ),
                },
                {
                    "step": 2,
                    "title": "Meet aviation requirements",
                    "description": (
                        "Meet the applicable medical "
                        "and aviation eligibility requirements."
                    ),
                },
                {
                    "step": 3,
                    "title": "Complete flight training",
                    "description": (
                        "Join an approved flight training "
                        "program and gain flight hours."
                    ),
                },
                {
                    "step": 4,
                    "title": "Obtain pilot license",
                    "description": (
                        "Complete the required examinations "
                        "and licensing process."
                    ),
                },
            ],
            "recommended_colleges": [],
        },
    },
]


async def seed_careers():

    async with AsyncSessionLocal() as session:

        inserted = 0
        skipped = 0

        for career in CAREERS:

            result = await session.execute(
                select(
                    CareerSearchKnowledge
                ).where(
                    CareerSearchKnowledge.query
                    == career["query"]
                )
            )

            existing = (
                result.scalar_one_or_none()
            )

            if existing:
                skipped += 1
                print(
                    f"Already exists: {career['query']}"
                )
                continue

            knowledge = CareerSearchKnowledge(
                query=career["query"],
                keywords=career["keywords"],
                result=career["result"],
                is_active=True,
            )

            session.add(knowledge)

            inserted += 1

            print(
                f"Inserted: {career['query']}"
            )

        await session.commit()

        print()
        print(
            f"Inserted: {inserted}"
        )
        print(
            f"Skipped: {skipped}"
        )


if __name__ == "__main__":
    asyncio.run(
        seed_careers()
    )