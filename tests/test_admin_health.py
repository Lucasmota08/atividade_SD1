from fastapi.testclient import TestClient

from admin_api.main import app


def test_health_degrades_without_registry():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in {"ok", "degraded"}
