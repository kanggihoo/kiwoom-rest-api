from datetime import datetime, timezone

import anyio
import pytest

from upbit_dashboard.api.errors import DashboardApiError
from upbit_dashboard.api.queries.quotation import QuotationReadService
from upbit_dashboard.contracts.errors import RestErrorCode
from upbit_dashboard.contracts.quotation import CandleUnit, StreamType, TickerData
from upbit_dashboard.contracts.rest import MarketSummary
from upbit_dashboard.state.market_state import MarketState
from upbit_dashboard.upbit.rest import UpbitCandleResponse


class FakeRestClient:
    def __init__(self) -> None:
        self.calls = []

    async def list_candles(self, *, unit: CandleUnit, market: str, count: int, to: str | None):
        self.calls.append({"unit": unit, "market": market, "count": count, "to": to})
        return [
            UpbitCandleResponse(
                market="KRW-BTC",
                candle_date_time_utc="2026-06-01T00:01:00",
                candle_date_time_kst="2026-06-01T09:01:00",
                opening_price=101.0,
                high_price=111.0,
                low_price=91.0,
                trade_price=106.0,
                candle_acc_trade_volume=2.0,
                candle_acc_trade_price=202000.0,
            ),
            UpbitCandleResponse(
                market="KRW-BTC",
                candle_date_time_utc="2026-06-01T00:00:00",
                candle_date_time_kst="2026-06-01T09:00:00",
                opening_price=100.0,
                high_price=110.0,
                low_price=90.0,
                trade_price=105.0,
                candle_acc_trade_volume=1.5,
                candle_acc_trade_price=150000.0,
            ),
        ]


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


def test_quotation_read_service_lists_candles_with_hidden_path_mapping() -> None:
    async def run_test() -> None:
        rest_client = FakeRestClient()
        service = QuotationReadService(
            market_catalogue=FakeMarketCatalogue(),
            upbit_rest_client=rest_client,
            market_state=MarketState(),
        )

        data = await service.list_candles(
            market=" krw-btc ",
            unit=CandleUnit.ONE_HOUR,
            count=2,
            to="2026-06-01T00:00:00Z",
        )

        assert rest_client.calls == [
            {
                "unit": CandleUnit.ONE_HOUR,
                "market": "KRW-BTC",
                "count": 2,
                "to": "2026-06-01T00:00:00Z",
            }
        ]
        assert data.market == "KRW-BTC"
        assert data.candle_unit is CandleUnit.ONE_HOUR
        assert [candle.candle_date_time_utc for candle in data.candles] == [
            "2026-06-01T00:00:00",
            "2026-06-01T00:01:00",
        ]

    anyio.run(run_test)


def test_quotation_read_service_rejects_non_krw_candle_market_before_upbit_call() -> None:
    async def run_test() -> None:
        rest_client = FakeRestClient()
        service = QuotationReadService(
            market_catalogue=FakeMarketCatalogue(),
            upbit_rest_client=rest_client,
            market_state=MarketState(),
        )

        with pytest.raises(DashboardApiError) as exc_info:
            await service.list_candles(
                market="USDT-BTC",
                unit=CandleUnit.ONE_MINUTE,
                count=1,
                to=None,
            )

        assert exc_info.value.code is RestErrorCode.BAD_REQUEST
        assert exc_info.value.status_code == 400
        assert exc_info.value.details == {"market": "USDT-BTC"}
        assert rest_client.calls == []

    anyio.run(run_test)


def test_quotation_read_service_returns_market_list_data() -> None:
    async def run_test() -> None:
        service = QuotationReadService(
            market_catalogue=FakeMarketCatalogue(),
            upbit_rest_client=FakeRestClient(),
            market_state=MarketState(),
        )

        data = await service.list_markets()

        assert [market.market for market in data.markets] == ["KRW-BTC"]

    anyio.run(run_test)


def test_quotation_read_service_returns_market_state_snapshot_data() -> None:
    state = MarketState()
    generated_at = datetime(2026, 6, 1, 3, 0, tzinfo=timezone.utc)
    state.upsert_ticker(_ticker("KRW-BTC"))
    service = QuotationReadService(
        market_catalogue=FakeMarketCatalogue(),
        upbit_rest_client=FakeRestClient(),
        market_state=state,
    )

    data = service.get_snapshot(generated_at=generated_at)

    assert data.generated_at == generated_at
    assert [ticker.market for ticker in data.tickers] == ["KRW-BTC"]
