import asyncio

from fastapi.testclient import TestClient

from upbit_dashboard.contracts.quotation import StreamType, TickerData
from upbit_dashboard.main import create_app


def _ticker(market: str) -> TickerData:
    return TickerData(
        market=market,
        opening_price=1.0,
        high_price=2.0,
        low_price=0.5,
        trade_price=1.5,
        signed_change_price=0.1,
        signed_change_rate=0.01,
        trade_volume=1.0,
        acc_trade_volume_24h=2.0,
        acc_trade_price_24h=3.0,
        trade_timestamp_ms=1,
        timestamp_ms=2,
        stream_type=StreamType.REALTIME,
    )


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


def test_lifespan_ticker_handler_updates_market_state_and_logs(monkeypatch) -> None:
    captured_kwargs = {}
    logged_markets: list[str] = []

    async def fake_run_ticker_stream(**kwargs) -> None:
        captured_kwargs.update(kwargs)
        await asyncio.Event().wait()

    async def fake_log_ticker(ticker: TickerData) -> None:
        logged_markets.append(ticker.market)

    monkeypatch.setenv("UPBIT_WS_ENABLED", "true")
    monkeypatch.setattr("upbit_dashboard.main.run_ticker_stream", fake_run_ticker_stream)
    monkeypatch.setattr("upbit_dashboard.main.log_ticker", fake_log_ticker)

    with TestClient(create_app()) as client:
        handler = captured_kwargs["on_ticker"]
        asyncio.run(handler(_ticker("KRW-BTC")))

        stored_ticker = client.app.state.market_state.get_ticker("KRW-BTC")
        assert stored_ticker is not None
        assert stored_ticker.trade_price == 1.5
        assert logged_markets == ["KRW-BTC"]
