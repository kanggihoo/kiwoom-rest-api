import pytest

from upbit_dashboard.tools.smoke_upbit_connection import validate_market_response


def test_validate_market_response_returns_market_count() -> None:
    data = [
        {"market": "KRW-BTC", "korean_name": "비트코인", "english_name": "Bitcoin"},
        {"market": "KRW-ETH", "korean_name": "이더리움", "english_name": "Ethereum"},
    ]

    assert validate_market_response(data) == 2


def test_validate_market_response_rejects_non_list() -> None:
    with pytest.raises(RuntimeError, match="list"):
        validate_market_response({"market": "KRW-BTC"})


def test_validate_market_response_rejects_items_without_market() -> None:
    with pytest.raises(RuntimeError, match="market"):
        validate_market_response([{"korean_name": "비트코인"}])

