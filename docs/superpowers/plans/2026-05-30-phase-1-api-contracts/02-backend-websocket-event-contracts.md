# 02 Backend WebSocket Event Contracts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Backend -> Frontend WebSocket event envelope와 `ticker:update`, `trade:update`, `orderbook:update`, `candle:update`, `alert:new` data 모델을 구현한다.

**Architecture:** `events.py`는 WebSocket event와 event data 모델만 책임진다. Python 내부는 snake_case, JSON 출력은 각 필드의 `serialization_alias`로 camelCase를 보장한다. REST 모델은 다음 단계에서 이 모델을 재사용한다.

**Tech Stack:** Python 3.12, Pydantic v2, pytest, RTK.

---

**순서:** 02 / 06
**이전 단계:** [01-backend-errors-and-enums.md](./01-backend-errors-and-enums.md)
**다음 단계:** [03-backend-rest-contracts.md](./03-backend-rest-contracts.md)

### Task 02: WebSocket 이벤트 계약 모델 추가

**Files:**
- Create: `apps/backend/src/upbit_dashboard/contracts/events.py`
- Create: `apps/backend/tests/test_contract_serialization.py`

- [ ] **Step 1: 실패하는 WebSocket 계약 테스트 작성**

`apps/backend/tests/test_contract_serialization.py`를 만든다.

```python
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from upbit_dashboard.contracts.events import (
    AlertData,
    AlertKind,
    AskBid,
    Candle,
    CandleUpdateData,
    CandleUpdateEvent,
    RealtimeCandleUnit,
    Severity,
    StreamType,
    TickerData,
    TickerUpdateEvent,
    TradeData,
    TradeUpdateEvent,
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
```

- [ ] **Step 2: 테스트 실패 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_contract_serialization.py -q
```

Expected:

```text
ModuleNotFoundError 또는 ImportError: events 모델이 아직 없음
```

- [ ] **Step 3: WebSocket event 모델 구현**

`apps/backend/src/upbit_dashboard/contracts/events.py`를 만든다.

```python
from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class StreamType(StrEnum):
    SNAPSHOT = "SNAPSHOT"
    REALTIME = "REALTIME"


class AskBid(StrEnum):
    ASK = "ASK"
    BID = "BID"


class CandleUnit(StrEnum):
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"


class RealtimeCandleUnit(StrEnum):
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"


class AlertKind(StrEnum):
    DAILY_RISE = "dailyRise"
    DAILY_DROP = "dailyDrop"
    SHORT_TERM_RISE = "shortTermRise"
    SHORT_TERM_DROP = "shortTermDrop"


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"


class TickerData(BaseModel):
    market: str = Field(description="Market 코드. Upbit ticker.code 기준.")
    opening_price: float = Field(serialization_alias="openingPrice", description="시가. Upbit ticker.opening_price 기준.")
    high_price: float = Field(serialization_alias="highPrice", description="고가. Upbit ticker.high_price 기준.")
    low_price: float = Field(serialization_alias="lowPrice", description="저가. Upbit ticker.low_price 기준.")
    trade_price: float = Field(serialization_alias="tradePrice", description="현재가. Upbit ticker.trade_price 기준.")
    signed_change_price: float = Field(serialization_alias="signedChangePrice", description="전일 대비 가격 변동 값. Upbit ticker.signed_change_price 기준.")
    signed_change_rate: float = Field(serialization_alias="signedChangeRate", description="전일 대비 등락률. Upbit ticker.signed_change_rate 기준.")
    trade_volume: float = Field(serialization_alias="tradeVolume", description="최근 거래량. Upbit ticker.trade_volume 기준.")
    acc_trade_volume_24h: float = Field(serialization_alias="accTradeVolume24h", description="최근 24시간 누적 거래량. Upbit ticker.acc_trade_volume_24h 기준.")
    acc_trade_price_24h: float = Field(serialization_alias="accTradePrice24h", description="최근 24시간 누적 거래대금. Upbit ticker.acc_trade_price_24h 기준.")
    trade_timestamp_ms: int = Field(serialization_alias="tradeTimestampMs", description="체결 타임스탬프(ms). Upbit ticker.trade_timestamp 기준.")
    timestamp_ms: int = Field(serialization_alias="timestampMs", description="Upbit 이벤트 타임스탬프(ms). Upbit ticker.timestamp 기준.")
    stream_type: StreamType = Field(serialization_alias="streamType", description="Upbit stream_type. SNAPSHOT 또는 REALTIME.")


class TradeData(BaseModel):
    market: str = Field(description="Market 코드. Upbit trade.code 기준.")
    trade_price: float = Field(serialization_alias="tradePrice", description="체결 가격. Upbit trade.trade_price 기준.")
    trade_volume: float = Field(serialization_alias="tradeVolume", description="체결량. Upbit trade.trade_volume 기준.")
    ask_bid: AskBid = Field(serialization_alias="askBid", description="매수/매도 구분. Upbit trade.ask_bid 기준.")
    trade_timestamp_ms: int = Field(serialization_alias="tradeTimestampMs", description="체결 타임스탬프(ms). Upbit trade.trade_timestamp 기준.")
    sequential_id: int = Field(serialization_alias="sequentialId", description="체결 번호. Upbit trade.sequential_id 기준.")
    timestamp_ms: int = Field(serialization_alias="timestampMs", description="Upbit 이벤트 타임스탬프(ms). Upbit trade.timestamp 기준.")
    stream_type: StreamType = Field(serialization_alias="streamType", description="Upbit stream_type. SNAPSHOT 또는 REALTIME.")


class OrderbookUnit(BaseModel):
    ask_price: float = Field(serialization_alias="askPrice", description="매도 호가. Upbit orderbook_units.ask_price 기준.")
    bid_price: float = Field(serialization_alias="bidPrice", description="매수 호가. Upbit orderbook_units.bid_price 기준.")
    ask_size: float = Field(serialization_alias="askSize", description="매도 잔량. Upbit orderbook_units.ask_size 기준.")
    bid_size: float = Field(serialization_alias="bidSize", description="매수 잔량. Upbit orderbook_units.bid_size 기준.")


class OrderbookData(BaseModel):
    market: str = Field(description="Market 코드. Upbit orderbook.code 기준.")
    total_ask_size: float = Field(serialization_alias="totalAskSize", description="매도 총 잔량. Upbit orderbook.total_ask_size 기준.")
    total_bid_size: float = Field(serialization_alias="totalBidSize", description="매수 총 잔량. Upbit orderbook.total_bid_size 기준.")
    level: float = Field(description="호가 모아보기 단위. Upbit orderbook.level 기준.")
    units: list[OrderbookUnit] = Field(description="호가 목록. Upbit orderbook.orderbook_units 기준.")
    timestamp_ms: int = Field(serialization_alias="timestampMs", description="Upbit 이벤트 타임스탬프(ms). Upbit orderbook.timestamp 기준.")
    stream_type: StreamType = Field(serialization_alias="streamType", description="Upbit stream_type. SNAPSHOT 또는 REALTIME.")


class Candle(BaseModel):
    candle_date_time_utc: str = Field(serialization_alias="candleDateTimeUtc", description="캔들 기준 시각 UTC. Upbit candle.candle_date_time_utc 기준.")
    candle_date_time_kst: str = Field(serialization_alias="candleDateTimeKst", description="캔들 기준 시각 KST. Upbit candle.candle_date_time_kst 기준.")
    opening_price: float = Field(serialization_alias="openingPrice", description="시가. Upbit candle.opening_price 기준.")
    high_price: float = Field(serialization_alias="highPrice", description="고가. Upbit candle.high_price 기준.")
    low_price: float = Field(serialization_alias="lowPrice", description="저가. Upbit candle.low_price 기준.")
    trade_price: float = Field(serialization_alias="tradePrice", description="종가. Upbit candle.trade_price 기준.")
    candle_acc_trade_volume: float = Field(serialization_alias="candleAccTradeVolume", description="누적 거래량. Upbit candle.candle_acc_trade_volume 기준.")
    candle_acc_trade_price: float = Field(serialization_alias="candleAccTradePrice", description="누적 거래금액. Upbit candle.candle_acc_trade_price 기준.")


class CandleUpdateData(BaseModel):
    market: str = Field(description="Market 코드.")
    candle_unit: RealtimeCandleUnit = Field(serialization_alias="candleUnit", description="실시간 candle 단위. 1m, 5m, 15m, 30m, 1h만 허용.")
    candle: Candle = Field(description="OHLCV candle 값.")
    timestamp_ms: int = Field(serialization_alias="timestampMs", description="Upbit candle WebSocket timestamp.")
    stream_type: StreamType = Field(serialization_alias="streamType", description="Upbit stream_type. SNAPSHOT 또는 REALTIME.")


class AlertData(BaseModel):
    id: str = Field(description="프론트 리스트 key와 중복 방지용 ID.")
    market: str = Field(description="Alert 대상 Market.")
    alert_kind: AlertKind = Field(serialization_alias="alertKind", description="Alert 종류.")
    title: str = Field(description="UI 표시 제목.")
    message: str = Field(description="UI 표시 메시지.")
    severity: Severity = Field(description="표시 심각도.")
    basis_rate: float = Field(serialization_alias="basisRate", description="Alert를 발생시킨 등락률.")
    basis_window: Literal["24h", "1m"] = Field(serialization_alias="basisWindow", description="Alert 계산 기준 구간.")
    created_at: datetime = Field(serialization_alias="createdAt", description="Alert 생성 시각.")


class TickerUpdateEvent(BaseModel):
    type: Literal["ticker:update"] = Field(default="ticker:update", description="Ticker update event type.")
    timestamp: datetime = Field(description="우리 서버가 이벤트를 만든 시각.")
    data: TickerData = Field(description="Ticker update payload.")


class TradeUpdateEvent(BaseModel):
    type: Literal["trade:update"] = Field(default="trade:update", description="Trade update event type.")
    timestamp: datetime = Field(description="우리 서버가 이벤트를 만든 시각.")
    data: TradeData = Field(description="Trade update payload.")


class OrderbookUpdateEvent(BaseModel):
    type: Literal["orderbook:update"] = Field(default="orderbook:update", description="Orderbook update event type.")
    timestamp: datetime = Field(description="우리 서버가 이벤트를 만든 시각.")
    data: OrderbookData = Field(description="Orderbook update payload.")


class CandleUpdateEvent(BaseModel):
    type: Literal["candle:update"] = Field(default="candle:update", description="Candle update event type.")
    timestamp: datetime = Field(description="우리 서버가 이벤트를 만든 시각.")
    data: CandleUpdateData = Field(description="Candle update payload.")


class AlertNewEvent(BaseModel):
    type: Literal["alert:new"] = Field(default="alert:new", description="Alert new event type.")
    timestamp: datetime = Field(description="우리 서버가 이벤트를 만든 시각.")
    data: AlertData = Field(description="Alert payload.")
```

- [ ] **Step 4: WebSocket 계약 테스트 통과 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_contract_serialization.py -q
```

Expected:

```text
5 passed
```

- [ ] **Step 5: 기존 에러 테스트 회귀 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_error_contracts.py apps/backend/tests/test_contract_serialization.py -q
```

Expected:

```text
9 passed
```

- [ ] **Step 6: 단계 커밋**

Run:

```bash
rtk git add apps/backend/src/upbit_dashboard/contracts/events.py apps/backend/tests/test_contract_serialization.py
rtk git commit -m "feat: add websocket event contract models"
```

Expected:

```text
커밋 생성
```
