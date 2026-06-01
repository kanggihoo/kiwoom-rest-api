# 01 Snapshot Route Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `GET /api/snapshot` FastAPI endpoint를 추가해 backend `MarketState`의 현재 ticker snapshot을 기존 REST Message envelope 계약으로 반환한다.

**Architecture:** 새 route module `api/routes/snapshot.py`가 `request.app.state.market_state`를 읽고, 응답 생성 시점의 UTC `now`를 envelope `timestamp`와 `data.generatedAt`에 동일하게 사용한다. `api/router.py`는 기존 health router와 snapshot router만 조합한다.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, pytest, TestClient, RTK.

---

**순서:** 01 / 04
**이전 단계:** 없음
**다음 단계:** [02-ticker-state-wiring.md](./02-ticker-state-wiring.md)

### Task 01: Snapshot route 추가

**Files:**
- Create: `apps/backend/tests/test_snapshot.py`
- Create: `apps/backend/src/upbit_dashboard/api/routes/snapshot.py`
- Modify: `apps/backend/src/upbit_dashboard/api/router.py`

- [ ] **Step 1: 실패하는 snapshot route 테스트 작성**

`apps/backend/tests/test_snapshot.py`를 만든다.

```python
from fastapi.testclient import TestClient

from upbit_dashboard.contracts.quotation import StreamType, TickerData
from upbit_dashboard.main import create_app


def _ticker(market: str) -> TickerData:
    return TickerData(
        market=market,
        opening_price=1.0,
        high_price=2.0,
        low_price=0.5,
        trade_price=1.5,
        signed_change_price=0.1,
        signed_change_rate=0.01,
        trade_volume=1.0,
        acc_trade_volume_24h=2.0,
        acc_trade_price_24h=3.0,
        trade_timestamp_ms=1,
        timestamp_ms=2,
        stream_type=StreamType.REALTIME,
    )


def test_snapshot_returns_empty_market_state(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")

    with TestClient(create_app()) as client:
        response = client.get("/api/snapshot")

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "market-state:snapshot"
    assert body["timestamp"] == body["data"]["generatedAt"]
    assert body["data"]["tickers"] == []
    assert "generated_at" not in body["data"]


def test_snapshot_returns_latest_ticker_data_with_aliases(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")
    app = create_app()
    app.state.market_state.upsert_ticker(_ticker("KRW-BTC"))

    with TestClient(app) as client:
        response = client.get("/api/snapshot")

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "market-state:snapshot"
    assert body["data"]["generatedAt"] == body["timestamp"]
    assert body["data"]["tickers"] == [
        {
            "market": "KRW-BTC",
            "openingPrice": 1.0,
            "highPrice": 2.0,
            "lowPrice": 0.5,
            "tradePrice": 1.5,
            "signedChangePrice": 0.1,
            "signedChangeRate": 0.01,
            "tradeVolume": 1.0,
            "accTradeVolume24h": 2.0,
            "accTradePrice24h": 3.0,
            "tradeTimestampMs": 1,
            "timestampMs": 2,
            "streamType": "REALTIME",
        }
    ]
    assert "trade_price" not in body["data"]["tickers"][0]
```

- [ ] **Step 2: 테스트 실패 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_snapshot.py -q
```

Expected:

```text
404 Not Found
```

- [ ] **Step 3: snapshot route 구현**

`apps/backend/src/upbit_dashboard/api/routes/snapshot.py`를 만든다.

```python
from datetime import datetime, timezone

from fastapi import APIRouter, Request

from upbit_dashboard.contracts.rest import (
    MarketStateSnapshotData,
    MarketStateSnapshotResponse,
)
from upbit_dashboard.state.market_state import MarketState

router = APIRouter()


@router.get("/api/snapshot", response_model=MarketStateSnapshotResponse)
def get_snapshot(request: Request) -> MarketStateSnapshotResponse:
    now = datetime.now(timezone.utc)
    market_state: MarketState = request.app.state.market_state
    snapshot = market_state.snapshot(generated_at=now)
    return MarketStateSnapshotResponse(
        timestamp=now,
        data=MarketStateSnapshotData(
            generated_at=snapshot.generated_at,
            tickers=list(snapshot.tickers),
        ),
    )
```

- [ ] **Step 4: snapshot router 등록**

`apps/backend/src/upbit_dashboard/api/router.py`를 다음처럼 수정한다.

```python
from fastapi import APIRouter

from upbit_dashboard.api.routes import health, snapshot

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(snapshot.router)
```

- [ ] **Step 5: snapshot route 테스트 통과 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_snapshot.py -q
```

Expected:

```text
2 passed
```

- [ ] **Step 6: 단계 커밋**

Run:

```bash
rtk proxy git add apps/backend/src/upbit_dashboard/api/router.py apps/backend/src/upbit_dashboard/api/routes/snapshot.py apps/backend/tests/test_snapshot.py
rtk proxy git commit -m "feat: expose backend market state snapshot"
```

Expected:

```text
커밋 생성
```
