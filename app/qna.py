from .ai_client import generate_text


def answer_question_with_gemini(question: str) -> str:
    """
    Answer a student's question using Gemini.
    """

    prompt = f"""
You are EduGenie, a friendly and helpful AI learning assistant.

Answer the student's question accurately and clearly.

Student question:
{question}

Instructions:
- Use simple language.
- Explain the answer clearly.
- Keep the response appropriate for a student.
- Give an example when useful.
- Do not invent facts.
- If the question is ambiguous, state the assumption.
"""

    return generate_text(
        prompt,
        temperature=0.3,
        max_output_tokens=800,
    )