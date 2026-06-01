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
    async def fake_run_ticker_stream(**kwargs) -> None:
        del kwargs
        await asyncio.Event().wait()

    monkeypatch.delenv("UPBIT_WS_ENABLED", raising=False)
    monkeypatch.setattr("upbit_dashboard.main.run_ticker_stream", fake_run_ticker_stream)

    with TestClient(create_app()) as client:
        assert client.app.state.upbit_ticker_task is not None
        assert client.app.state.upbit_ticker_task.done() is False


def test_lifespan_passes_settings_to_upbit_stream(monkeypatch) -> None:
    captured_kwargs = {}

    async def fake_run_ticker_stream(**kwargs) -> None:
        captured_kwargs.update(kwargs)
        await asyncio.Event().wait()

    monkeypatch.setenv("UPBIT_WS_ENABLED", "true")
    monkeypatch.setenv("UPBIT_TICKER_MARKETS", "KRW-XRP,KRW-ETH")
    monkeypatch.setenv("UPBIT_WS_ENDPOINT", "wss://example.test/ws")
    monkeypatch.setenv("UPBIT_TICKET", "local-ticket")
    monkeypatch.setenv("UPBIT_INITIAL_BACKOFF_SECONDS", "2")
    monkeypatch.setenv("UPBIT_MAX_BACKOFF_SECONDS", "16")
    monkeypatch.setattr("upbit_dashboard.main.run_ticker_stream", fake_run_ticker_stream)

    with TestClient(create_app()) as client:
        assert client.app.state.upbit_ticker_task is not None
        assert captured_kwargs["markets"] == ("KRW-XRP", "KRW-ETH")
        assert captured_kwargs["endpoint"] == "wss://example.test/ws"
        assert captured_kwargs["ticket"] == "local-ticket"
        assert captured_kwargs["initial_backoff"] == 2.0
        assert captured_kwargs["max_backoff"] == 16.0
