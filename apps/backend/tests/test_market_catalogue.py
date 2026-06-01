import pytest

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
