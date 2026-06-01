import pytest

from upbit_dashboard.market.catalogue import normalize_krw_market_codes
from upbit_dashboard.upbit.client import build_ticker_subscription
from upbit_dashboard.settings import (
    DEFAULT_TICKER_MARKETS,
    DEFAULT_TICKET,
    DEFAULT_UPBIT_WS_ENDPOINT,
)


def test_default_upbit_phase2_settings_are_fixed() -> None:
    assert DEFAULT_UPBIT_WS_ENDPOINT == "wss://api.upbit.com/websocket/v1"
    assert DEFAULT_TICKER_MARKETS == ("KRW-BTC", "KRW-ETH")
    assert DEFAULT_TICKET == "upbit-dashboard-phase2"


def test_normalize_krw_market_codes_trims_and_uppercases_codes() -> None:
    assert normalize_krw_market_codes([" krw-btc ", "krw-eth"]) == ("KRW-BTC", "KRW-ETH")


def test_build_ticker_subscription_uses_default_format_and_codes() -> None:
    message = build_ticker_subscription([" krw-btc ", "KRW-ETH"])

    assert message == [
        {"ticket": "upbit-dashboard-phase2"},
        {"type": "ticker", "codes": ["KRW-BTC", "KRW-ETH"]},
        {"format": "DEFAULT"},
    ]


def test_build_ticker_subscription_rejects_non_krw_markets() -> None:
    with pytest.raises(ValueError, match="KRW"):
        build_ticker_subscription(["USDT-BTC"])
