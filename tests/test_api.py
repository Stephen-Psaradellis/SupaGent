from fastapi.testclient import TestClient

from app.main import build_app


def test_query_endpoint_returns_answer_and_sources():
    app = build_app()
    client = TestClient(app)

    # The default VectorStore may be empty, so mock the route by monkeypatching app state if needed.
    # For now, we just ensure the endpoint accepts input and returns required keys.
    resp = client.post("/query", json={"question": "Test question"})
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "sources" in data
