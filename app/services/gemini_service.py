
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
        api_key = os.getenv("GEMINI_API_KEY", "").strip()

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing from the backend environment."
            )

        self.client = genai.Client(api_key=api_key)

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        ).strip()

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

IMPORTANT RULES

1. CURRENT GOAL
The student's current goal is the primary career direction.
Never replace a clear goal with an old career goal from the database.

2. EDUCATIONAL CONTEXT
Use profile only to understand age, education, and class_year.
Do not let old career_goal, career_interests, or institution fields
override the current goal.

3. STUDENT ANSWERS
Use answers to understand interests, strengths, preferences,
favorite subjects, and motivation.
Answers may refine but must not override a clear career goal.

4. CURRENT STAGE
Match current_stage to the student's actual education.
For example:
- School + Class 9 -> Class 9
- Bachelor's Degree + Final Year -> Final Year College Student
Never invent an education stage.

5. RECOMMENDED STREAM
Match the stream to the career:
- Doctor: PCB with Biology
- AI Engineer: PCM with Computer Science
- Software Engineer: PCM with Computer Science
- Lawyer: Humanities / Law pathway
- CA: Commerce

For graduates, recommend relevant higher studies or professional
training instead of incorrectly treating them as school students.

6. TARGET EXAMS
Recommend only exams relevant to the career and current stage.
Examples:
- Medicine: NEET-UG
- Engineering: JEE Main, JEE Advanced, BITSAT, VITEEE
- Law: CLAT, AILET
Do not recommend irrelevant exams.

7. ROADMAP
Provide six logical steps starting from the student's current stage.
For school students, progress through school, stream selection,
entrance preparation, college, specialization, and career.
For college students or graduates, begin with their current
education, then relevant skills, projects, internships or placements,
entry-level work, and career growth as appropriate.

8. RECOMMENDED COLLEGES
Recommend colleges relevant to the student's career and location
when known. Never recommend engineering colleges to a medical
student or vice versa. Do not invent admission requirements.

9. CONFIDENCE SCORE
Return a number between 0 and 100.

10. OUTPUT FORMAT
Return only valid JSON.
Do not return Markdown or code fences.
Do not add explanations outside the JSON.

CURRENT STUDENT GOAL:
{goal}

EDUCATIONAL CONTEXT:
{json.dumps(profile, indent=2, ensure_ascii=False)}

STUDENT ANSWERS:
{json.dumps(answers, indent=2, ensure_ascii=False)}

RETURN EXACTLY THIS JSON STRUCTURE:

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

            response_text = response.text.strip()

            # Remove Markdown code fences if present.
            if response_text.startswith("```json"):
                response_text = response_text[len("```json"):].strip()
            elif response_text.startswith("```"):
                response_text = response_text[len("```"):].strip()

            if response_text.endswith("```"):
                response_text = response_text[:-3].strip()

            # Parse JSON.
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "Gemini returned invalid JSON."
                ) from exc

            if not isinstance(result, dict):
                raise ValueError(
                    "Gemini response must be a JSON object."
                )

            # Validate required fields.
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

            # Validate confidence score.
            confidence = result["confidence_score"]

            if (
                isinstance(confidence, bool)
                or not isinstance(confidence, (int, float))
            ):
                raise ValueError(
                    "confidence_score must be a number."
                )

            if not 0 <= confidence <= 100:
                raise ValueError(
                    "confidence_score must be between 0 and 100."
                )

            # Validate collection fields.
            if not isinstance(result["target_exams"], list):
                raise ValueError("target_exams must be a list.")

            if not isinstance(result["roadmap"], list):
                raise ValueError("roadmap must be a list.")

            if not isinstance(result["recommended_colleges"], list):
                raise ValueError("recommended_colleges must be a list.")

            if len(result["roadmap"]) != 6:
                raise ValueError("roadmap must contain exactly six steps.")

            return result

        except Exception as exc:
            raise ValueError(
                f"AI career generation failed: {exc}"
            ) from exc
