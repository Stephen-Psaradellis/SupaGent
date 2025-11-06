import os
from fastapi.testclient import TestClient

from app.main import build_app
from tools.ingest import ingest_simple_folder


def test_end_to_end_ingest_then_query(tmp_path):
    # Arrange: create a small dataset
    ds = tmp_path / "dataset"
    ds.mkdir()
    (ds / "passwords.md").write_text("Reset your password via Settings.")
    (ds / "shipping.txt").write_text("Shipping delays occur during holidays.")

    # Ingest into a temp persist dir
    os.environ["CHROMA_PERSIST_DIR"] = str(tmp_path / "chroma")
    ingest_simple_folder(str(ds))

    # Spin API using the same persist dir
    app = build_app()
    client = TestClient(app)

    # Act
    resp = client.post("/query", json={"question": "How do I reset my password?"})
    assert resp.status_code == 200
    data = resp.json()

    # Assert
    assert "answer" in data and "sources" in data
    assert any("password" in (s.get("title", "").lower()) for s in data["sources"])