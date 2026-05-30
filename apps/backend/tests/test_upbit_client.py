import json

from pydantic import ValidationError
import pytest

from upbit_dashboard.contracts.quotation import StreamType
from upbit_dashboard.upbit.client import UpbitWebSocketError, parse_ticker_payload


def _ticker_payload() -> dict[str, object]:
    return {
        "type": "ticker",
        "code": "KRW-BTC",
        "opening_price": 108000000,
        "high_price": 109000000,
        "low_price": 107500000,
        "trade_price": 108359000,
        "signed_change_price": -106000,
        "signed_change_rate": -0.001,
        "trade_volume": 0.01,
        "acc_trade_volume_24h": 1288.5,
        "acc_trade_price_24h": 139663338391,
        "trade_timestamp": 1760000000000,
        "timestamp": 1760000000100,
        "stream_type": "REALTIME",
    }


def test_parse_ticker_payload_converts_bytes_to_ticker_data() -> None:
    payload = json.dumps(_ticker_payload()).encode("utf-8")

    ticker = parse_ticker_payload(payload)

    assert ticker.market == "KRW-BTC"
    assert ticker.trade_price == 108359000
    assert ticker.trade_timestamp_ms == 1760000000000
    assert ticker.stream_type is StreamType.REALTIME


def test_parse_ticker_payload_serializes_with_frontend_aliases() -> None:
    ticker = parse_ticker_payload(json.dumps(_ticker_payload()))

    dumped = ticker.model_dump(mode="json", by_alias=True)

    assert dumped["market"] == "KRW-BTC"
    assert dumped["tradePrice"] == 108359000
    assert dumped["streamType"] == "REALTIME"
    assert "trade_price" not in dumped


def test_parse_ticker_payload_rejects_upbit_error_payload() -> None:
    payload = {
        "error": {
            "name": "NO_CODES",
            "message": "codes field is required",
        }
    }

    with pytest.raises(UpbitWebSocketError) as exc_info:
        parse_ticker_payload(json.dumps(payload))

    assert exc_info.value.name == "NO_CODES"
    assert "codes field is required" in str(exc_info.value)


def test_parse_ticker_payload_rejects_non_object_json() -> None:
    with pytest.raises(ValueError, match="JSON object"):
        parse_ticker_payload("[1, 2, 3]")


def test_parse_ticker_payload_rejects_invalid_ticker_shape() -> None:
    payload = _ticker_payload()
    payload.pop("trade_price")

    with pytest.raises(ValidationError):
        parse_ticker_payload(json.dumps(payload))

