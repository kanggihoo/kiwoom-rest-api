import pytest

from kiwoom_rest_api.kiwoom_smoke import (
    KiwoomConfig,
    build_stock_info_request,
    mask_secret,
    parse_price,
)


def test_mask_secret_keeps_only_edges():
    assert mask_secret("abcdefghijklmnopqrstuvwxyz") == "abcd...wxyz"


def test_mask_secret_handles_short_values():
    assert mask_secret("abc") == "***"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("+156600", 156600),
        ("-78800", 78800),
        ("121700", 121700),
        ("", None),
        (None, None),
    ],
)
def test_parse_price_normalizes_kiwoom_price_strings(raw, expected):
    assert parse_price(raw) == expected


def test_build_stock_info_request_uses_ka10095_contract():
    config = KiwoomConfig(
        app_key="app-key",
        app_secret_key="secret-key",
        base_url="https://api.kiwoom.com",
        stock_code="005930",
        timeout_seconds=10.0,
    )

    url, headers, body = build_stock_info_request(config, "token-value")

    assert url == "https://api.kiwoom.com/api/dostk/stkinfo"
    assert headers["api-id"] == "ka10095"
    assert headers["authorization"] == "Bearer token-value"
    assert body == {"stk_cd": "005930"}
