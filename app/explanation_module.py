from .ai_client import generate_text


def explain_topic(topic: str) -> str:
    """
    Explain a topic in simple language.
    """

    prompt = f"""
You are EduGenie, an AI tutor.

Explain the following topic to a school or college student:

Topic:
{topic}

Requirements:
- Start with a simple definition.
- Explain the concept clearly.
- Use simple language.
- Give a short example or analogy when useful.
- Mention important points.
- Avoid unnecessary jargon.
- Keep the answer concise.
"""

    return generate_text(
        prompt,
        temperature=0.5,
        max_output_tokens=900,
    )