from upbit_dashboard.upbit.client import build_ticker_subscription, normalize_markets
from upbit_dashboard.upbit.settings import (
    DEFAULT_TICKER_MARKETS,
    DEFAULT_TICKET,
    DEFAULT_UPBIT_WS_ENDPOINT,
    is_upbit_ws_enabled,
)


def test_default_upbit_phase2_settings_are_fixed() -> None:
    assert DEFAULT_UPBIT_WS_ENDPOINT == "wss://api.upbit.com/websocket/v1"
    assert DEFAULT_TICKER_MARKETS == ("KRW-BTC", "KRW-ETH")
    assert DEFAULT_TICKET == "upbit-dashboard-phase2"


def test_is_upbit_ws_enabled_defaults_to_true() -> None:
    assert is_upbit_ws_enabled(None) is True
    assert is_upbit_ws_enabled("") is True
    assert is_upbit_ws_enabled("true") is True
    assert is_upbit_ws_enabled("TRUE") is True


def test_is_upbit_ws_enabled_accepts_false_values() -> None:
    assert is_upbit_ws_enabled("false") is False
    assert is_upbit_ws_enabled("0") is False
    assert is_upbit_ws_enabled("off") is False
    assert is_upbit_ws_enabled("no") is False


def test_normalize_markets_trims_and_uppercases_codes() -> None:
    assert normalize_markets([" krw-btc ", "krw-eth"]) == ("KRW-BTC", "KRW-ETH")


def test_build_ticker_subscription_uses_default_format_and_codes() -> None:
    message = build_ticker_subscription([" krw-btc ", "KRW-ETH"])

    assert message == [
        {"ticket": "upbit-dashboard-phase2"},
        {"type": "ticker", "codes": ["KRW-BTC", "KRW-ETH"]},
        {"format": "DEFAULT"},
    ]

