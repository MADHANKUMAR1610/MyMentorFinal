# app/services/gemini_service.py

import json
import os
from typing import Any

from dotenv import load_dotenv
from google import genai


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


class GeminiService:

    # ========================================================
    # INITIALIZE GEMINI
    # ========================================================

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured. "
                "Please add GEMINI_API_KEY to your .env file."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.6-flash"
        )

    # ========================================================
    # GENERATE CAREER PERSONA
    # ========================================================

    async def generate_career_persona(
        self,
        goal: str,
        profile: dict[str, Any],
        answers: dict[str, Any],
    ) -> dict[str, Any]:

        prompt = f"""
You are an expert AI career guidance engine for MyMentor.

Generate a personalized career roadmap for the student.

============================================================
IMPORTANT RULES
============================================================

1. CURRENT GOAL IS THE PRIMARY CAREER DIRECTION

The student's current goal must control the recommended
career.

Example:

Student goal:
"I want to become a doctor"

The career MUST remain related to:

- Doctor
- Medicine
- Medical field
- Medical specialization

Do NOT change the career to Software Engineer because
the database contains an old career_goal.

------------------------------------------------------------

2. PROFILE IS ONLY EDUCATIONAL CONTEXT

Use profile ONLY to understand:

- age
- education
- class_year

Do NOT use these old profile fields to override the
student's current goal:

- career_goal
- career_interests
- institution

The current student goal has priority.

------------------------------------------------------------

3. STUDENT ANSWERS

Use answers to understand:

- interests
- strengths
- preferences
- favorite subjects
- motivation

Answers can refine the recommendation but must not override
a clear career goal.

------------------------------------------------------------

4. CURRENT STAGE

The current_stage MUST match the student's actual education.

Example:

education = "School"
class_year = "Class 9"

Then:

current_stage = "Class 9"

Example:

education = "Bachelor's Degree"
class_year = "Final Year"

Then:

current_stage = "Final Year College Student"

NEVER invent Class 9 when the student is actually in college.

------------------------------------------------------------

5. RECOMMENDED STREAM

The recommended stream MUST match the career.

Doctor:
PCB with Biology

AI Engineer:
PCM with Computer Science

Software Engineer:
PCM with Computer Science

Lawyer:
Humanities / Law pathway

CA:
Commerce

------------------------------------------------------------

6. TARGET EXAMS

Target exams MUST match the career and current stage.

Medicine:

NEET-UG

Engineering:

JEE Main
JEE Advanced
BITSAT
VITEEE

Law:

CLAT
AILET

Do NOT recommend irrelevant exams.

------------------------------------------------------------

7. ROADMAP

The roadmap MUST start from the student's current stage.

For Class 9:

Class 9-10
→ Class 11-12
→ Entrance Exam
→ Medical/Engineering/Law College
→ Specialization
→ Career

For final-year college:

Final Year
→ Placement / Higher Studies
→ Entry-Level Job
→ Specialization
→ Career Growth

------------------------------------------------------------

8. RECOMMENDED COLLEGES

Recommended colleges MUST match the career.

Medical goal:
Recommend medical colleges.

Engineering goal:
Recommend engineering colleges.

Law goal:
Recommend law colleges.

Do NOT recommend engineering colleges to a medical student.

------------------------------------------------------------

9. CONFIDENCE SCORE

Return a number between 0 and 100.

------------------------------------------------------------

10. OUTPUT FORMAT

Return ONLY valid JSON.

Do NOT return markdown.

Do NOT return ```json.

Do NOT add explanations outside JSON.

============================================================
CURRENT STUDENT GOAL
============================================================

{goal}

============================================================
EDUCATIONAL CONTEXT
============================================================

{json.dumps(profile, indent=2)}

============================================================
STUDENT ANSWERS
============================================================

{json.dumps(answers, indent=2)}

============================================================
RETURN EXACTLY THIS JSON STRUCTURE
============================================================

{{
    "career_persona": "string",

    "career": "string",

    "current_stage": "string",

    "recommended_stream": "string",

    "confidence_score": 0,

    "career_overview": "string",

    "recommended_next_step": "string",

    "primary_skill": "string",

    "target_exams": [
        "string"
    ],

    "roadmap": [
        {{
            "step": 1,
            "title": "string",
            "stage": "string",
            "description": "string"
        }},
        {{
            "step": 2,
            "title": "string",
            "stage": "string",
            "description": "string"
        }},
        {{
            "step": 3,
            "title": "string",
            "stage": "string",
            "description": "string"
        }},
        {{
            "step": 4,
            "title": "string",
            "stage": "string",
            "description": "string"
        }},
        {{
            "step": 5,
            "title": "string",
            "stage": "string",
            "description": "string"
        }},
        {{
            "step": 6,
            "title": "string",
            "stage": "string",
            "description": "string"
        }}
    ],

    "recommended_colleges": [
        {{
            "name": "string",
            "location": "string",
            "type": "Government or Private",
            "admission": "string"
        }}
    ]
}}
"""

        try:

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )

            if not response or not response.text:
                raise ValueError(
                    "Gemini returned an empty response."
                )

            text = response.text.strip()

            # =================================================
            # REMOVE MARKDOWN CODE FENCES
            # =================================================

            if text.startswith("```json"):
                text = text[len("```json"):]

            elif text.startswith("```"):
                text = text[len("```"):]

            if text.endswith("```"):
                text = text[:-3]

            text = text.strip()

            # =================================================
            # PARSE JSON
            # =================================================

            try:

                result = json.loads(text)

            except json.JSONDecodeError as exc:

                raise ValueError(
                    f"Gemini returned invalid JSON:\n{text}"
                ) from exc

            # =================================================
            # REQUIRED FIELDS
            # =================================================

            required_fields = [
                "career_persona",
                "career",
                "current_stage",
                "recommended_stream",
                "confidence_score",
                "career_overview",
                "recommended_next_step",
                "primary_skill",
                "target_exams",
                "roadmap",
                "recommended_colleges",
            ]

            missing_fields = [
                field
                for field in required_fields
                if field not in result
            ]

            if missing_fields:

                raise ValueError(
                    "Gemini response is missing fields: "
                    + ", ".join(missing_fields)
                )

            # =================================================
            # VALIDATE CONFIDENCE SCORE
            # =================================================

            confidence = result.get(
                "confidence_score"
            )

            if not isinstance(
                confidence,
                (int, float)
            ):
                raise ValueError(
                    "confidence_score must be a number."
                )

            if confidence < 0 or confidence > 100:
                raise ValueError(
                    "confidence_score must be between 0 and 100."
                )

            return result

        except Exception as exc:

            raise ValueError(
                f"AI career generation failed: {exc}"
            ) from exc