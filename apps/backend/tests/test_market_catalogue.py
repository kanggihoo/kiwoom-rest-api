import pytest

from upbit_dashboard.market.catalogue import assert_krw_market, is_krw_market, parse_market_code


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
