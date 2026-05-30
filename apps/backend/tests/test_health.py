from fastapi.testclient import TestClient

from upbit_dashboard.main import create_app


def test_health_returns_ok(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "upbit-dashboard-backend",
    }
