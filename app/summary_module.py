from .ai_client import generate_text


def summarize_text(text: str) -> str:
    """
    Summarize supplied text.
    """

    prompt = f"""
You are EduGenie, an educational AI assistant.

Summarize the following text in simple language.

Rules:
- Preserve the main idea.
- Preserve important facts.
- Do not invent information.
- Remove unnecessary repetition.
- Use short paragraphs or bullet points when appropriate.

Text:
{text}
"""

    return generate_text(
        prompt,
        temperature=0.2,
        max_output_tokens=900,
    )