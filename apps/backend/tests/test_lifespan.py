import asyncio

from fastapi.testclient import TestClient

from upbit_dashboard.main import create_app


def test_lifespan_skips_upbit_stream_when_disabled(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")

    with TestClient(create_app()) as client:
        response = client.get("/health")

        assert response.status_code == 200
        assert client.app.state.upbit_ticker_task is None


def test_lifespan_starts_upbit_stream_by_default(monkeypatch) -> None:
    async def fake_run_ticker_stream() -> None:
        await asyncio.Event().wait()

    monkeypatch.delenv("UPBIT_WS_ENABLED", raising=False)
    monkeypatch.setattr("upbit_dashboard.main.run_ticker_stream", fake_run_ticker_stream)

    with TestClient(create_app()) as client:
        assert client.app.state.upbit_ticker_task is not None
        assert client.app.state.upbit_ticker_task.done() is False

