# 04 Upbit Ticker Raw And Mapper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Phase 2에서 바로 사용할 Upbit ticker 원본 Pydantic 모델과 `TickerData` 변환 mapper를 구현한다.

**Architecture:** `upbit.py`는 Upbit 원본 메시지 모델만 둔다. `mappers.py`는 Upbit raw 모델을 앱 계약 모델로 바꾸는 순수 함수만 둔다. Phase 1에서는 ticker raw만 구현하고 trade/orderbook/candle raw 모델은 만들지 않는다.

**Tech Stack:** Python 3.12, Pydantic v2, pytest, RTK.

---

**순서:** 04 / 06
**이전 단계:** [03-backend-rest-contracts.md](./03-backend-rest-contracts.md)
**다음 단계:** [05-frontend-contract-types.md](./05-frontend-contract-types.md)

### Task 04: Upbit ticker raw 모델과 mapper 추가

**Files:**
- Create: `apps/backend/src/upbit_dashboard/contracts/upbit.py`
- Create: `apps/backend/src/upbit_dashboard/contracts/mappers.py`
- Create: `apps/backend/tests/test_upbit_ticker_mapper.py`

- [ ] **Step 1: 실패하는 mapper 테스트 작성**

`apps/backend/tests/test_upbit_ticker_mapper.py`를 만든다.

```python
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
```

- [ ] **Step 2: 테스트 실패 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_upbit_ticker_mapper.py -q
```

Expected:

```text
ImportError: cannot import name 'map_upbit_ticker_message'
```

- [ ] **Step 3: Upbit ticker raw 모델 구현**

`apps/backend/src/upbit_dashboard/contracts/upbit.py`를 만든다.

```python
from typing import Literal

from pydantic import BaseModel, Field


class UpbitTickerMessage(BaseModel):
    type: Literal["ticker"] = Field(description="Upbit WebSocket 데이터 항목. ticker.")
    code: str = Field(description="Upbit Market 코드. 예: KRW-BTC.")
    opening_price: float = Field(description="시가. Upbit ticker.opening_price.")
    high_price: float = Field(description="고가. Upbit ticker.high_price.")
    low_price: float = Field(description="저가. Upbit ticker.low_price.")
    trade_price: float = Field(description="현재가. Upbit ticker.trade_price.")
    signed_change_price: float = Field(description="전일 대비 가격 변동 값. Upbit ticker.signed_change_price.")
    signed_change_rate: float = Field(description="전일 대비 등락률. Upbit ticker.signed_change_rate.")
    trade_volume: float = Field(description="최근 거래량. Upbit ticker.trade_volume.")
    acc_trade_volume_24h: float = Field(description="최근 24시간 누적 거래량. Upbit ticker.acc_trade_volume_24h.")
    acc_trade_price_24h: float = Field(description="최근 24시간 누적 거래대금. Upbit ticker.acc_trade_price_24h.")
    trade_timestamp: int = Field(description="체결 타임스탬프(ms). Upbit ticker.trade_timestamp.")
    timestamp: int = Field(description="이벤트 타임스탬프(ms). Upbit ticker.timestamp.")
    stream_type: Literal["SNAPSHOT", "REALTIME"] = Field(description="Upbit stream_type.")
```

- [ ] **Step 4: mapper 구현**

`apps/backend/src/upbit_dashboard/contracts/mappers.py`를 만든다.

```python
from upbit_dashboard.contracts.events import StreamType, TickerData
from upbit_dashboard.contracts.upbit import UpbitTickerMessage


def map_upbit_ticker_message(message: UpbitTickerMessage) -> TickerData:
    return TickerData(
        market=message.code,
        opening_price=message.opening_price,
        high_price=message.high_price,
        low_price=message.low_price,
        trade_price=message.trade_price,
        signed_change_price=message.signed_change_price,
        signed_change_rate=message.signed_change_rate,
        trade_volume=message.trade_volume,
        acc_trade_volume_24h=message.acc_trade_volume_24h,
        acc_trade_price_24h=message.acc_trade_price_24h,
        trade_timestamp_ms=message.trade_timestamp,
        timestamp_ms=message.timestamp,
        stream_type=StreamType(message.stream_type),
    )
```

- [ ] **Step 5: mapper 테스트 통과 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_upbit_ticker_mapper.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 6: 전체 백엔드 계약 테스트 실행**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_error_contracts.py apps/backend/tests/test_contract_serialization.py apps/backend/tests/test_upbit_ticker_mapper.py -q
```

Expected:

```text
15 passed
```

- [ ] **Step 7: 단계 커밋**

Run:

```bash
rtk git add apps/backend/src/upbit_dashboard/contracts/upbit.py apps/backend/src/upbit_dashboard/contracts/mappers.py apps/backend/tests/test_upbit_ticker_mapper.py
rtk git commit -m "feat: add upbit ticker contract mapper"
```

Expected:

```text
커밋 생성
```
