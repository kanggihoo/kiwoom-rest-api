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


def test_snapshot_returns_empty_market_state(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")

    with TestClient(create_app()) as client:
        response = client.get("/api/snapshot")

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "market-state:snapshot"
    assert body["timestamp"] == body["data"]["generatedAt"]
    assert body["data"]["tickers"] == []
    assert "generated_at" not in body["data"]


def test_snapshot_returns_latest_ticker_data_with_aliases(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")
    app = create_app()
    app.state.market_state.upsert_ticker(_ticker("KRW-BTC"))

    with TestClient(app) as client:
        response = client.get("/api/snapshot")

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "market-state:snapshot"
    assert body["data"]["generatedAt"] == body["timestamp"]
    assert body["data"]["tickers"] == [
        {
            "market": "KRW-BTC",
            "openingPrice": 1.0,
            "highPrice": 2.0,
            "lowPrice": 0.5,
            "tradePrice": 1.5,
            "signedChangePrice": 0.1,
            "signedChangeRate": 0.01,
            "tradeVolume": 1.0,
            "accTradeVolume24h": 2.0,
            "accTradePrice24h": 3.0,
            "tradeTimestampMs": 1,
            "timestampMs": 2,
            "streamType": "REALTIME",
        }
    ]
    assert "trade_price" not in body["data"]["tickers"][0]
