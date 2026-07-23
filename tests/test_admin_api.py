from fastapi.testclient import TestClient

from admin_api.main import app


def test_logs_endpoint_returns_entries():
    response = TestClient(app).get("/logs?limit=2")
    assert response.status_code == 200
    assert response.json()["limit"] == 2


def test_docs_endpoint_exists():
    assert TestClient(app).get("/docs").status_code == 200
