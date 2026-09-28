from .ai_client import generate_text


def get_learning_recommendations(topic: str) -> str:
    """
    Generate a structured learning path for a topic.
    """

    prompt = f"""
You are EduGenie, an adaptive AI learning assistant.

The student wants to learn:

{topic}

Create a practical learning path.

Include:

1. Beginner level
2. Intermediate level
3. Advanced level
4. Recommended practice activities
5. Common mistakes to avoid
6. A simple suggested study sequence

Make the plan easy to understand and suitable for a student.

Do not invent specific external resources unless you are confident
they exist.
"""

    return generate_text(
        prompt,
        temperature=0.5,
        max_output_tokens=1400,
    )