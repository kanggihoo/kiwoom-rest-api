from fastapi.testclient import TestClient

from upbit_dashboard.api.dependencies import get_quotation_read_service
from upbit_dashboard.contracts.quotation import Candle, CandleUnit
from upbit_dashboard.contracts.rest import CandlesListData
from upbit_dashboard.main import create_app


class FakeQuotationReadService:
    def __init__(self) -> None:
        self.calls = []

    async def list_candles(self, *, market: str, unit: CandleUnit, count: int, to: str | None):
        self.calls.append({"market": market, "unit": unit, "count": count, "to": to})
        return CandlesListData(
            market="KRW-BTC",
            candle_unit=unit,
            candles=[
                Candle(
                    candle_date_time_utc="2026-06-01T00:00:00",
                    candle_date_time_kst="2026-06-01T09:00:00",
                    opening_price=100.0,
                    high_price=110.0,
                    low_price=90.0,
                    trade_price=105.0,
                    candle_acc_trade_volume=1.5,
                    candle_acc_trade_price=150000.0,
                ),
                Candle(
                    candle_date_time_utc="2026-06-01T00:01:00",
                    candle_date_time_kst="2026-06-01T09:01:00",
                    opening_price=101.0,
                    high_price=111.0,
                    low_price=91.0,
                    trade_price=106.0,
                    candle_acc_trade_volume=2.0,
                    candle_acc_trade_price=202000.0,
                ),
            ],
        )


def test_candles_route_delegates_query_and_returns_envelope(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")
    app = create_app()
    fake_service = FakeQuotationReadService()
    app.dependency_overrides[get_quotation_read_service] = lambda: fake_service

    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/candles",
                params={
                    "market": "KRW-BTC",
                    "unit": "1h",
                    "count": "2",
                    "to": "2026-06-01T00:00:00Z",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert fake_service.calls == [
        {
            "market": "KRW-BTC",
            "unit": CandleUnit.ONE_HOUR,
            "count": 2,
            "to": "2026-06-01T00:00:00Z",
        }
    ]
    body = response.json()
    assert body["type"] == "candles:list"
    assert body["data"]["market"] == "KRW-BTC"
    assert body["data"]["candleUnit"] == "1h"
    assert [candle["candleDateTimeUtc"] for candle in body["data"]["candles"]] == [
        "2026-06-01T00:00:00",
        "2026-06-01T00:01:00",
    ]


def test_candles_route_uses_default_count_200(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")
    app = create_app()
    fake_service = FakeQuotationReadService()
    app.dependency_overrides[get_quotation_read_service] = lambda: fake_service

    try:
        with TestClient(app) as client:
            response = client.get("/api/candles?market=KRW-BTC&unit=1m")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert fake_service.calls[0]["count"] == 200


def test_candles_route_rejects_count_above_200(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")

    with TestClient(create_app()) as client:
        response = client.get("/api/candles?market=KRW-BTC&unit=1m&count=201")

    assert response.status_code == 422


def test_candles_route_rejects_invalid_to_query_before_service_call(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")
    app = create_app()
    fake_service = FakeQuotationReadService()
    app.dependency_overrides[get_quotation_read_service] = lambda: fake_service

    try:
        with TestClient(app) as client:
            response = client.get("/api/candles?market=KRW-BTC&unit=1m&to=not-a-date")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert fake_service.calls == []


def test_candles_route_rejects_non_krw_market(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")

    with TestClient(create_app()) as client:
        response = client.get("/api/candles?market=USDT-BTC&unit=1m")

    assert response.status_code == 400
    assert response.json()["type"] == "error"
    assert response.json()["data"]["code"] == "BAD_REQUEST"
