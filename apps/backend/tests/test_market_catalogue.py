import pytest
from datetime import datetime, timedelta, timezone

import anyio
from upbit_dashboard.contracts.rest import MarketSummary
from upbit_dashboard.market.catalogue import MarketCatalogueService, map_upbit_market_summary
from upbit_dashboard.upbit.rest import UpbitMarketResponse, UpbitRestError

from upbit_dashboard.market.catalogue import (
    assert_krw_market,
    is_krw_market,
    normalize_krw_market_codes,
    parse_market_code,
    parse_market_code_list,
    parse_krw_market_code_list,
)


def test_parse_market_code_normalizes_and_splits_components() -> None:
    market = parse_market_code("krw-btc")
    assert market.quote_currency == "KRW"
    assert market.base_currency == "BTC"
    assert market.as_upbit_code() == "KRW-BTC"


def test_parse_market_code_rejects_invalid_pattern() -> None:
    with pytest.raises(ValueError):
        parse_market_code("krwbTC")


def test_assert_krw_market_blocks_non_krw_pairs() -> None:
    assert is_krw_market("KRW-BTC") is True
    with pytest.raises(ValueError):
        assert_krw_market("USDT-BTC")


def test_parse_market_code_list_normalizes_comma_separated_values() -> None:
    assert parse_market_code_list(" krw-btc,KRW-XRP, ,krw-eth ", default=("KRW-BTC",)) == (
        "KRW-BTC",
        "KRW-XRP",
        "KRW-ETH",
    )


def test_parse_market_code_list_uses_default_for_blank_input() -> None:
    assert parse_market_code_list("  ", default=("KRW-BTC", "KRW-ETH")) == (
        "KRW-BTC",
        "KRW-ETH",
    )


def test_normalize_krw_market_codes_rejects_empty_and_non_krw_markets() -> None:
    with pytest.raises(ValueError, match="At least one"):
        normalize_krw_market_codes([" ", ""])

    with pytest.raises(ValueError, match="KRW"):
        normalize_krw_market_codes(["USDT-BTC"])


def test_parse_krw_market_code_list_rejects_non_krw_markets() -> None:
    with pytest.raises(ValueError, match="KRW"):
        parse_krw_market_code_list("KRW-BTC,USDT-ETH", default=("KRW-BTC",))


class FakeMarketClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    async def list_markets(self):
        self.calls += 1
        result = self.responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


def test_map_upbit_market_summary_filters_and_maps_krw_market() -> None:
    summary = map_upbit_market_summary(
        UpbitMarketResponse(
            market="KRW-BTC",
            korean_name="비트코인",
            english_name="Bitcoin",
        )
    )

    assert summary == MarketSummary(
        market="KRW-BTC",
        korean_name="비트코인",
        english_name="Bitcoin",
        quote_currency="KRW",
        base_currency="BTC",
    )


def test_market_catalogue_service_filters_krw_and_caches_fresh_result() -> None:
    async def run_test() -> None:
        client = FakeMarketClient(
            [
                [
                    UpbitMarketResponse(market="KRW-BTC", korean_name="비트코인", english_name="Bitcoin"),
                    UpbitMarketResponse(market="USDT-BTC", korean_name="비트코인", english_name="Bitcoin"),
                ]
            ]
        )
        service = MarketCatalogueService(client=client, ttl_seconds=600)
        now = datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc)

        first = await service.list_krw_markets(now=now)
        second = await service.list_krw_markets(now=now + timedelta(seconds=10))

        assert [market.market for market in first] == ["KRW-BTC"]
        assert second == first
        assert client.calls == 1

    anyio.run(run_test)


def test_market_catalogue_service_refreshes_expired_cache() -> None:
    async def run_test() -> None:
        client = FakeMarketClient(
            [
                [UpbitMarketResponse(market="KRW-BTC", korean_name="비트코인", english_name="Bitcoin")],
                [UpbitMarketResponse(market="KRW-ETH", korean_name="이더리움", english_name="Ethereum")],
            ]
        )
        service = MarketCatalogueService(client=client, ttl_seconds=600)
        now = datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc)

        await service.list_krw_markets(now=now)
        refreshed = await service.list_krw_markets(now=now + timedelta(seconds=601))

        assert [market.market for market in refreshed] == ["KRW-ETH"]
        assert client.calls == 2

    anyio.run(run_test)


def test_market_catalogue_service_returns_stale_on_refresh_failure() -> None:
    async def run_test() -> None:
        client = FakeMarketClient(
            [
                [UpbitMarketResponse(market="KRW-BTC", korean_name="비트코인", english_name="Bitcoin")],
                UpbitRestError(status_code=502, message="Upbit failed"),
            ]
        )
        service = MarketCatalogueService(client=client, ttl_seconds=600)
        now = datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc)

        await service.list_krw_markets(now=now)
        stale = await service.list_krw_markets(now=now + timedelta(seconds=601))

        assert [market.market for market in stale] == ["KRW-BTC"]
        assert client.calls == 2

    anyio.run(run_test)
