import os

os.environ["MOCK_AI"] = "true"


from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():

    response = client.get(
        "/api/health"
    )

    assert response.status_code == 200

    assert (
        response.json()["status"]
        == "ok"
    )


def test_qna():

    response = client.post(
        "/api/qna",
        json={
            "text": "What is AI?"
        },
    )

    assert response.status_code == 200

    assert "answer" in response.json()


def test_qga_compatibility():

    response = client.post(
        "/api/qga",
        json={
            "text": "What is Python?"
        },
    )

    assert response.status_code == 200

    assert "answer" in response.json()


def test_explain():

    response = client.post(
        "/api/explain",
        json={
            "text": "Photosynthesis",
            "level": "beginner",
        },
    )

    assert response.status_code == 200

    assert (
        "explanation"
        in response.json()
    )


def test_summarize():

    response = client.post(
        "/api/summarize",
        json={
            "text": (
                "Plants use sunlight "
                "to make food."
            )
        },
    )

    assert response.status_code == 200

    assert (
        "summary"
        in response.json()
    )


def test_quiz():

    response = client.post(
        "/api/quiz",
        json={
            "topic": "Fractions",
            "num_questions": 3,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(
        body["questions"]
    ) == 3

    assert all(
        len(question["options"]) == 4
        for question
        in body["questions"]
    )


def test_recommendations():

    response = client.post(
        "/api/learn/recommendations",
        json={
            "topic": "Algebra",
            "interests": [
                "coding"
            ],
        },
    )

    assert response.status_code == 200

    assert len(
        response.json()[
            "recommendations"
        ]
    ) == 3