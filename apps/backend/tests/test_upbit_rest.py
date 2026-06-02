from __future__ import annotations

import anyio
import httpx
import pytest

from upbit_dashboard.contracts.quotation import CandleUnit
from upbit_dashboard.upbit.rest import (
    UpbitRestClient,
    UpbitRestError,
)


def test_list_markets_returns_raw_market_models() -> None:
    async def run_test() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/market/all"
            assert request.url.params["is_details"] == "false"
            return httpx.Response(
                200,
                json=[
                    {
                        "market": "KRW-BTC",
                        "korean_name": "비트코인",
                        "english_name": "Bitcoin",
                    }
                ],
            )

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="https://api.upbit.com") as http_client:
            client = UpbitRestClient(http_client=http_client)
            markets = await client.list_markets()

        assert markets[0].market == "KRW-BTC"
        assert markets[0].korean_name == "비트코인"
        assert markets[0].english_name == "Bitcoin"

    anyio.run(run_test)


def test_list_candles_returns_raw_candle_models() -> None:
    async def run_test() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/candles/minutes/1"
            assert request.url.params["market"] == "KRW-BTC"
            assert request.url.params["count"] == "2"
            return httpx.Response(
                200,
                json=[
                    {
                        "market": "KRW-BTC",
                        "candle_date_time_utc": "2026-06-01T00:01:00",
                        "candle_date_time_kst": "2026-06-01T09:01:00",
                        "opening_price": 100.0,
                        "high_price": 110.0,
                        "low_price": 90.0,
                        "trade_price": 105.0,
                        "candle_acc_trade_volume": 1.5,
                        "candle_acc_trade_price": 150000.0,
                    }
                ],
            )

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="https://api.upbit.com") as http_client:
            client = UpbitRestClient(http_client=http_client)
            candles = await client.list_candles(
                unit=CandleUnit.ONE_MINUTE,
                market="KRW-BTC",
                count=2,
                to=None,
            )

        assert candles[0].market == "KRW-BTC"
        assert candles[0].trade_price == 105.0

    anyio.run(run_test)


def test_list_candles_uses_candle_unit_specific_upbit_path() -> None:
    async def run_test() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/candles/minutes/60"
            return httpx.Response(200, json=[])

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="https://api.upbit.com") as http_client:
            client = UpbitRestClient(http_client=http_client)
            candles = await client.list_candles(
                unit=CandleUnit.ONE_HOUR,
                market="KRW-BTC",
                count=2,
                to=None,
            )

        assert candles == []

    anyio.run(run_test)


def test_upbit_error_response_raises_typed_error() -> None:
    async def run_test() -> None:
        def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(
                429,
                headers={"Remaining-Req": "group=candle; min=1800; sec=0"},
                json={"error": {"name": 429, "message": "Too many requests"}},
            )

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="https://api.upbit.com") as http_client:
            client = UpbitRestClient(http_client=http_client)
            with pytest.raises(UpbitRestError) as exc_info:
                await client.list_markets()

        assert exc_info.value.status_code == 429
        assert exc_info.value.remaining_req == "group=candle; min=1800; sec=0"
        assert exc_info.value.error_name == "429"

    anyio.run(run_test)

