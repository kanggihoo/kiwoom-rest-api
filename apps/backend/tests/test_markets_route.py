from fastapi.testclient import TestClient

from upbit_dashboard.api.dependencies import get_quotation_read_service
from upbit_dashboard.contracts.rest import MarketSummary, MarketsListData
from upbit_dashboard.main import create_app


class FakeMarketCatalogue:
    async def list_krw_markets(self):
        return (
            MarketSummary(
                market="KRW-BTC",
                korean_name="비트코인",
                english_name="Bitcoin",
                quote_currency="KRW",
                base_currency="BTC",
            ),
        )


class FakeQuotationReadService:
    async def list_markets(self):
        return MarketsListData(markets=list(await FakeMarketCatalogue().list_krw_markets()))


def test_markets_route_returns_market_metadata(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")
    app = create_app()
    app.dependency_overrides[get_quotation_read_service] = lambda: FakeQuotationReadService()

    try:
        with TestClient(app) as client:
            response = client.get("/api/markets")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "markets:list"
    assert body["data"]["markets"] == [
        {
            "market": "KRW-BTC",
            "koreanName": "비트코인",
            "englishName": "Bitcoin",
            "quoteCurrency": "KRW",
            "baseCurrency": "BTC",
        }
    ]
