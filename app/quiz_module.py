from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, Field

from .ai_client import generate_structured, generate_text
from .config import get_settings


class QuizQuestion(BaseModel):
    """
    One multiple-choice question.
    """

    question: str = Field(
        min_length=1,
        description="The quiz question."
    )

    options: list[str] = Field(
        min_length=4,
        max_length=4,
        description="Exactly four answer options."
    )

    answer: str = Field(
        min_length=1,
        description="The correct answer. Must match one option."
    )


def clean_json_block(text: str) -> str:
    """
    Remove Markdown JSON fences if Gemini returns them.
    """

    text = text.strip()

    match = re.search(
        r"```(?:json)?\s*(.*?)\s*```",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    return text


def validate_quiz(data: Any) -> list[dict[str, Any]]:
    """
    Validate and normalize Gemini quiz output.
    """

    if isinstance(data, list):
        raw_items = data

    elif isinstance(data, dict) and "questions" in data:
        raw_items = data["questions"]

    else:
        raise ValueError(
            "Quiz response must be a JSON array."
        )

    if not isinstance(raw_items, list):
        raise ValueError(
            "Quiz questions must be a list."
        )

    valid_questions: list[dict[str, Any]] = []

    for item in raw_items:
        if isinstance(item, QuizQuestion):
            question = item

        elif isinstance(item, dict):
            try:
                question = QuizQuestion.model_validate(item)
            except Exception:
                continue

        else:
            continue

        options = [
            option.strip()
            for option in question.options
            if isinstance(option, str) and option.strip()
        ]

        answer = question.answer.strip()

        if len(options) != 4:
            continue

        if answer not in options:
            continue

        valid_questions.append(
            {
                "question": question.question.strip(),
                "options": options,
                "answer": answer,
            }
        )

    if len(valid_questions) < 3:
        raise ValueError(
            "Gemini did not return three valid quiz questions."
        )

    return valid_questions[:3]


def generate_quiz(text: str) -> list[dict[str, Any]]:
    """
    Generate exactly three MCQ questions.
    """

    settings = get_settings()

    prompt = f"""
You are EduGenie, an educational quiz generator.

Create exactly 3 multiple-choice questions from the passage below.

Each question must contain:

- question
- options: exactly 4 options
- answer: exactly one of the four options

Rules:
- Questions must be based only on the supplied passage.
- Avoid ambiguous questions.
- Use one correct answer.
- Make distractors plausible.
- Do not include explanations.
- Return exactly 3 questions.

Passage:
{text}
"""

    # Use the structured Gemini response when real AI is enabled.
    if not settings.mock_ai:
        try:
            structured = generate_structured(
                prompt,
                list[QuizQuestion],
                temperature=0.4,
                max_output_tokens=1400,
            )

            if structured is not None:
                return validate_quiz(structured)

        except Exception:
            # Fall back to normal JSON generation below.
            pass

    # Mock mode or fallback mode.
    raw = generate_text(
        prompt
        + """

Return ONLY valid JSON.
Do not use Markdown.
""",
        temperature=0.4,
        max_output_tokens=1400,
    )

    try:
        parsed = json.loads(
            clean_json_block(raw)
        )

        return validate_quiz(parsed)

    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(
            f"Could not parse Gemini quiz response: {exc}"
        ) from exc