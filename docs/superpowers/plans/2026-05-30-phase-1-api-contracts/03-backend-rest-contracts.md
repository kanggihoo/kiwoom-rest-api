# 03 Backend REST Contracts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `markets:list`, `market-state:snapshot`, `candles:list` REST response envelope와 data 모델을 구현한다.

**Architecture:** `rest.py`는 REST 성공 응답 계약만 책임진다. `TickerData`, `Candle`, `CandleUnit`은 `events.py`의 타입을 재사용해 REST와 WebSocket의 data 구조 차이를 최소화한다.

**Tech Stack:** Python 3.12, Pydantic v2, pytest, RTK.

---

**순서:** 03 / 06
**이전 단계:** [02-backend-websocket-event-contracts.md](./02-backend-websocket-event-contracts.md)
**다음 단계:** [04-upbit-ticker-raw-and-mapper.md](./04-upbit-ticker-raw-and-mapper.md)

### Task 03: REST 응답 계약 모델 추가

**Files:**
- Create: `apps/backend/src/upbit_dashboard/contracts/rest.py`
- Modify: `apps/backend/tests/test_contract_serialization.py`

- [ ] **Step 1: 실패하는 REST 계약 테스트 추가**

`apps/backend/tests/test_contract_serialization.py` 아래에 다음 테스트를 추가한다.

```python
from upbit_dashboard.contracts.events import CandleUnit
from upbit_dashboard.contracts.rest import (
    CandlesListData,
    CandlesListResponse,
    MarketStateSnapshotData,
    MarketStateSnapshotResponse,
    MarketSummary,
    MarketsListData,
    MarketsListResponse,
)


def test_markets_list_response_serializes_market_metadata() -> None:
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


def test_candles_list_keeps_market_and_unit_at_data_level() -> None:
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
```

- [ ] **Step 2: 테스트 실패 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_contract_serialization.py -q
```

Expected:

```text
ImportError: cannot import name 'MarketsListResponse'
```

- [ ] **Step 3: REST 계약 모델 구현**

`apps/backend/src/upbit_dashboard/contracts/rest.py`를 만든다.

```python
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from upbit_dashboard.contracts.events import Candle, CandleUnit, TickerData


class MarketSummary(BaseModel):
    market: str = Field(description="Upbit Market 코드. 예: KRW-BTC.")
    korean_name: str = Field(serialization_alias="koreanName", description="한글 Market 이름.")
    english_name: str = Field(serialization_alias="englishName", description="영문 Market 이름.")
    quote_currency: str = Field(serialization_alias="quoteCurrency", description="기준 통화. 예: KRW.")
    base_currency: str = Field(serialization_alias="baseCurrency", description="대상 자산. 예: BTC.")


class MarketsListData(BaseModel):
    markets: list[MarketSummary] = Field(description="Market 메타데이터 목록.")


class MarketsListResponse(BaseModel):
    type: Literal["markets:list"] = Field(default="markets:list", description="Market metadata list response type.")
    timestamp: datetime = Field(description="우리 서버가 응답을 만든 시각.")
    data: MarketsListData = Field(description="Market metadata list payload.")


class MarketStateSnapshotData(BaseModel):
    generated_at: datetime = Field(serialization_alias="generatedAt", description="백엔드 MarketState snapshot 생성 시각.")
    tickers: list[TickerData] = Field(description="최신 ticker 목록. ticker:update.data와 같은 구조.")


class MarketStateSnapshotResponse(BaseModel):
    type: Literal["market-state:snapshot"] = Field(default="market-state:snapshot", description="MarketState snapshot response type.")
    timestamp: datetime = Field(description="우리 서버가 응답을 만든 시각.")
    data: MarketStateSnapshotData = Field(description="MarketState snapshot payload.")


class CandlesListData(BaseModel):
    market: str = Field(description="Market 코드.")
    candle_unit: CandleUnit = Field(serialization_alias="candleUnit", description="앱 candle 단위.")
    candles: list[Candle] = Field(description="candleDateTimeUtc 오름차순 candle 목록.")


class CandlesListResponse(BaseModel):
    type: Literal["candles:list"] = Field(default="candles:list", description="Candles list response type.")
    timestamp: datetime = Field(description="우리 서버가 응답을 만든 시각.")
    data: CandlesListData = Field(description="Candles list payload.")
```

- [ ] **Step 4: REST 계약 테스트 통과 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_contract_serialization.py -q
```

Expected:

```text
8 passed
```

- [ ] **Step 5: 에러 계약 회귀 포함 백엔드 계약 테스트 실행**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_error_contracts.py apps/backend/tests/test_contract_serialization.py -q
```

Expected:

```text
12 passed
```

- [ ] **Step 6: 단계 커밋**

Run:

```bash
rtk git add apps/backend/src/upbit_dashboard/contracts/rest.py apps/backend/tests/test_contract_serialization.py
rtk git commit -m "feat: add rest response contract models"
```

Expected:

```text
커밋 생성
```
