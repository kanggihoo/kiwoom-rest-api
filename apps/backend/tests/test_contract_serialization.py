from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from upbit_dashboard.contracts.events import (
    AlertData,
    AlertKind,
    CandleUpdateData,
    CandleUpdateEvent,
    RealtimeCandleUnit,
    Severity,
    TickerUpdateEvent,
    TradeUpdateEvent,
)
from upbit_dashboard.contracts.quotation import (
    AskBid,
    Candle,
    CandleUnit,
    StreamType,
    TickerData,
    TradeData,
)
from upbit_dashboard.contracts.rest import (
    CandlesListData,
    CandlesListResponse,
    MarketStateSnapshotData,
    MarketStateSnapshotResponse,
    MarketSummary,
    MarketsListData,
    MarketsListResponse,
)


def test_ticker_update_event_serializes_with_camel_case_aliases() -> None:
    event = TickerUpdateEvent(
        timestamp=datetime(2026, 5, 30, 3, 0, tzinfo=timezone.utc),
        data=TickerData(
            market="KRW-BTC",
            opening_price=108000000,
            high_price=109000000,
            low_price=107500000,
            trade_price=108359000,
            signed_change_price=-106000,
            signed_change_rate=-0.001,
            trade_volume=0.01,
            acc_trade_volume_24h=1288.5,
            acc_trade_price_24h=139663338391,
            trade_timestamp_ms=1760000000000,
            timestamp_ms=1760000000100,
            stream_type=StreamType.REALTIME,
        ),
    )

    dumped = event.model_dump(mode="json", by_alias=True)

    assert dumped["type"] == "ticker:update"
    assert dumped["data"]["tradePrice"] == 108359000
    assert dumped["data"]["signedChangeRate"] == -0.001
    assert dumped["data"]["accTradePrice24h"] == 139663338391
    assert dumped["data"]["tradeTimestampMs"] == 1760000000000
    assert "trade_price" not in dumped["data"]


def test_trade_update_event_uses_selected_market_trade_fields() -> None:
    event = TradeUpdateEvent(
        timestamp=datetime(2026, 5, 30, 3, 0, tzinfo=timezone.utc),
        data=TradeData(
            market="KRW-BTC",
            trade_price=108359000,
            trade_volume=0.01,
            ask_bid=AskBid.BID,
            trade_timestamp_ms=1760000000000,
            sequential_id=123456789,
            timestamp_ms=1760000000100,
            stream_type=StreamType.REALTIME,
        ),
    )

    dumped = event.model_dump(mode="json", by_alias=True)

    assert dumped["type"] == "trade:update"
    assert dumped["data"]["askBid"] == "BID"
    assert dumped["data"]["sequentialId"] == 123456789


def test_candle_update_rejects_non_realtime_candle_unit() -> None:
    with pytest.raises(ValidationError):
        CandleUpdateData(
            market="KRW-BTC",
            candle_unit="1d",
            candle=Candle(
                candle_date_time_utc="2026-05-30T03:00:00Z",
                candle_date_time_kst="2026-05-30T12:00:00+09:00",
                opening_price=108000000,
                high_price=109000000,
                low_price=107500000,
                trade_price=108359000,
                candle_acc_trade_volume=12.34,
                candle_acc_trade_price=139663338391,
            ),
            timestamp_ms=1760000000100,
            stream_type=StreamType.REALTIME,
        )


def test_candle_update_event_serializes_nested_candle() -> None:
    event = CandleUpdateEvent(
        timestamp=datetime(2026, 5, 30, 3, 0, tzinfo=timezone.utc),
        data=CandleUpdateData(
            market="KRW-BTC",
            candle_unit=RealtimeCandleUnit.ONE_MINUTE,
            candle=Candle(
                candle_date_time_utc="2026-05-30T03:00:00Z",
                candle_date_time_kst="2026-05-30T12:00:00+09:00",
                opening_price=108000000,
                high_price=109000000,
                low_price=107500000,
                trade_price=108359000,
                candle_acc_trade_volume=12.34,
                candle_acc_trade_price=139663338391,
            ),
            timestamp_ms=1760000000100,
            stream_type=StreamType.REALTIME,
        ),
    )

    dumped = event.model_dump(mode="json", by_alias=True)

    assert dumped["type"] == "candle:update"
    assert dumped["data"]["candleUnit"] == "1m"
    assert dumped["data"]["candle"]["candleDateTimeUtc"] == "2026-05-30T03:00:00Z"
    assert "candle_unit" not in dumped["data"]


def test_alert_new_event_schema_contains_field_descriptions() -> None:
    schema = AlertData.model_json_schema(mode="serialization")

    assert schema["properties"]["alertKind"]["description"]
    assert schema["properties"]["basisRate"]["description"]
    assert AlertKind.DAILY_RISE.value == "dailyRise"
    assert Severity.WARNING.value == "warning"


def test_markets_snapshot_response_serializes_market_metadata() -> None:
    response = MarketsListResponse(
        timestamp=datetime(2026, 5, 30, 3, 0, tzinfo=timezone.utc),
        data=MarketsListData(
            markets=[
                MarketSummary(
                    market="KRW-BTC",
                    korean_name="비트코인",
                    english_name="Bitcoin",
                    quote_currency="KRW",
                    base_currency="BTC",
                )
            ],
        ),
    )

    dumped = response.model_dump(mode="json", by_alias=True)

    assert dumped["type"] == "markets:list"
    assert dumped["data"]["markets"][0] == {
        "market": "KRW-BTC",
        "koreanName": "비트코인",
        "englishName": "Bitcoin",
        "quoteCurrency": "KRW",
        "baseCurrency": "BTC",
    }


def test_market_state_snapshot_reuses_ticker_data_shape() -> None:
    ticker = TickerData(
        market="KRW-BTC",
        opening_price=108000000,
        high_price=109000000,
        low_price=107500000,
        trade_price=108359000,
        signed_change_price=-106000,
        signed_change_rate=-0.001,
        trade_volume=0.01,
        acc_trade_volume_24h=1288.5,
        acc_trade_price_24h=139663338391,
        trade_timestamp_ms=1760000000000,
        timestamp_ms=1760000000100,
        stream_type=StreamType.REALTIME,
    )
    response = MarketStateSnapshotResponse(
        timestamp=datetime(2026, 5, 30, 3, 0, tzinfo=timezone.utc),
        data=MarketStateSnapshotData(
            generated_at=datetime(2026, 5, 30, 3, 0, tzinfo=timezone.utc),
            tickers=[ticker],
        ),
    )

    dumped = response.model_dump(mode="json", by_alias=True)

    assert dumped["type"] == "market-state:snapshot"
    assert dumped["data"]["generatedAt"] == "2026-05-30T03:00:00Z"
    assert dumped["data"]["tickers"][0]["tradePrice"] == 108359000


def test_candles_snapshot_keeps_market_and_unit_at_data_level() -> None:
    response = CandlesListResponse(
        timestamp=datetime(2026, 5, 30, 3, 0, tzinfo=timezone.utc),
        data=CandlesListData(
            market="KRW-BTC",
            candle_unit=CandleUnit.ONE_MINUTE,
            candles=[
                Candle(
                    candle_date_time_utc="2026-05-30T03:00:00Z",
                    candle_date_time_kst="2026-05-30T12:00:00+09:00",
                    opening_price=108000000,
                    high_price=109000000,
                    low_price=107500000,
                    trade_price=108359000,
                    candle_acc_trade_volume=12.34,
                    candle_acc_trade_price=139663338391,
                )
            ],
        ),
    )

    dumped = response.model_dump(mode="json", by_alias=True)

    assert dumped["type"] == "candles:list"
    assert dumped["data"]["candleUnit"] == "1m"
    assert "market" not in dumped["data"]["candles"][0]
    assert "candleUnit" not in dumped["data"]["candles"][0]


def test_events_module_does_not_reexport_quotation_models() -> None:
    import upbit_dashboard.contracts.events as events

    assert not hasattr(events, "StreamType")
    assert not hasattr(events, "CandleUnit")
    assert not hasattr(events, "AskBid")
