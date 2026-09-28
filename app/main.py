from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from .ai_client import AIServiceError
from .config import get_settings
from .explanation_module import explain_topic
from .learning_path import get_learning_recommendations
from .qna import answer_question_with_gemini
from .quiz_module import generate_quiz
from .summary_module import summarize_text


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

settings = get_settings()

BASE_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "EduGenie is a Google Gemini powered learning assistant "
        "for questions, explanations, summaries, quizzes and "
        "adaptive learning recommendations."
    ),
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Static files and templates
# ---------------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


# ---------------------------------------------------------
# Request models
# ---------------------------------------------------------

class TextRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        description="Text supplied by the student.",
    )


class TopicRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=1,
        description="Topic supplied by the student.",
    )


# ---------------------------------------------------------
# Error handlers
# ---------------------------------------------------------

@app.exception_handler(AIServiceError)
async def ai_error_handler(
    _: Request,
    exc: AIServiceError,
):
    return JSONResponse(
        status_code=503,
        content={
            "error": str(exc)
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(
    _: Request,
    exc: ValueError,
):
    return JSONResponse(
        status_code=502,
        content={
            "error": str(exc)
        },
    )


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def clean_input(
    value: str,
    field_name: str,
) -> str:
    """
    Validate user input.
    """

    value = value.strip()

    if not value:
        raise ValueError(
            f"Please provide {field_name}."
        )

    if len(value) > settings.max_input_chars:
        raise ValueError(
            f"{field_name.capitalize()} is too long. "
            f"Maximum allowed length is "
            f"{settings.max_input_chars} characters."
        )

    return value


# ---------------------------------------------------------
# Frontend
# ---------------------------------------------------------

@app.get(
    "/",
    include_in_schema=False,
)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "mock_ai": settings.mock_ai,
        "model": settings.gemini_model,
    }


# ---------------------------------------------------------
# Q&A
# ---------------------------------------------------------

@app.get("/qna")
@app.get("/qga")
async def answer_question(
    question: str = Query(
        ...,
        min_length=1,
        description="Student question.",
    )
):
    question = clean_input(
        question,
        "a question",
    )

    answer = answer_question_with_gemini(
        question
    )

    return {
        "question": question,
        "answer": answer,
    }


# ---------------------------------------------------------
# Explanation
# ---------------------------------------------------------

@app.post("/explain")
@app.post("/explain/")
async def explain_api(
    payload: TopicRequest,
):
    topic = clean_input(
        payload.topic,
        "a topic",
    )

    explanation = explain_topic(
        topic
    )

    return {
        "topic": topic,
        "explanation": explanation,
    }


# ---------------------------------------------------------
# Summarization
# ---------------------------------------------------------

@app.post("/summarize")
@app.post("/summarize/")
async def summarize_api(
    payload: TextRequest,
):
    text = clean_input(
        payload.text,
        "text to summarize",
    )

    summary = summarize_text(
        text
    )

    return {
        "summary": summary,
    }


# ---------------------------------------------------------
# Quiz
# ---------------------------------------------------------

@app.post("/quiz")
@app.post("/quiz/")
async def quiz_api(
    payload: TextRequest,
):
    text = clean_input(
        payload.text,
        "text for quiz",
    )

    quiz = generate_quiz(
        text
    )

    return {
        "quiz": quiz,
    }


# ---------------------------------------------------------
# Learning recommendations
# ---------------------------------------------------------

@app.get(
    "/learn/recommendations"
)
@app.get(
    "/learn/recommendations/"
)
async def learning_recommendation_api(
    topic: str = Query(
        ...,
        min_length=1,
    )
):
    topic = clean_input(
        topic,
        "a topic",
    )

    recommendation = (
        get_learning_recommendations(
            topic
        )
    )

    return {
        "topic": topic,
        "recommendation": recommendation,
    }