from pydantic import ValidationError
import pytest

from upbit_dashboard.contracts.events import StreamType
from upbit_dashboard.contracts.mappers import map_upbit_ticker_message
from upbit_dashboard.contracts.upbit import UpbitTickerMessage


def test_upbit_ticker_message_maps_to_app_ticker_data() -> None:
    message = UpbitTickerMessage(
        type="ticker",
        code="KRW-BTC",
        opening_price=108000000,
        high_price=109000000,
        low_price=107500000,
        trade_price=108359000,
        signed_change_price=-106000,
        signed_change_rate=-0.001,
        trade_volume=0.01,
        acc_trade_volume_24h=1288.5,
        acc_trade_price_24h=139663338391,
        trade_timestamp=1760000000000,
        timestamp=1760000000100,
        stream_type="REALTIME",
    )

    ticker = map_upbit_ticker_message(message)

    assert ticker.market == "KRW-BTC"
    assert ticker.trade_price == 108359000
    assert ticker.signed_change_rate == -0.001
    assert ticker.trade_timestamp_ms == 1760000000000
    assert ticker.timestamp_ms == 1760000000100
    assert ticker.stream_type is StreamType.REALTIME


def test_mapped_ticker_serializes_for_frontend_contract() -> None:
    message = UpbitTickerMessage(
        type="ticker",
        code="KRW-BTC",
        opening_price=108000000,
        high_price=109000000,
        low_price=107500000,
        trade_price=108359000,
        signed_change_price=-106000,
        signed_change_rate=-0.001,
        trade_volume=0.01,
        acc_trade_volume_24h=1288.5,
        acc_trade_price_24h=139663338391,
        trade_timestamp=1760000000000,
        timestamp=1760000000100,
        stream_type="REALTIME",
    )

    dumped = map_upbit_ticker_message(message).model_dump(mode="json", by_alias=True)

    assert dumped["market"] == "KRW-BTC"
    assert dumped["tradePrice"] == 108359000
    assert dumped["accTradeVolume24h"] == 1288.5
    assert dumped["streamType"] == "REALTIME"


def test_upbit_ticker_message_rejects_non_ticker_type() -> None:
    with pytest.raises(ValidationError):
        UpbitTickerMessage(
            type="trade",
            code="KRW-BTC",
            opening_price=108000000,
            high_price=109000000,
            low_price=107500000,
            trade_price=108359000,
            signed_change_price=-106000,
            signed_change_rate=-0.001,
            trade_volume=0.01,
            acc_trade_volume_24h=1288.5,
            acc_trade_price_24h=139663338391,
            trade_timestamp=1760000000000,
            timestamp=1760000000100,
            stream_type="REALTIME",
        )
