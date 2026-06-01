# 03 Candles Route Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** FastAPI `GET /api/candles`를 추가해 선택 Market의 candle history를 Upbit REST에서 가져오고 앱 계약의 오름차순 `candles:list`로 반환한다.

**Architecture:** Route는 query parameter validation과 REST envelope 생성을 담당한다. Upbit candle path mapping과 raw candle -> `Candle` 변환은 작고 테스트 가능한 함수로 둔다. Candle 응답은 cache/state에 저장하지 않는다.

**Tech Stack:** Python 3.12, FastAPI Query, Pydantic v2, pytest, RTK.

---

**순서:** 03 / 07  
**이전 단계:** [02-market-catalogue-route.md](./02-market-catalogue-route.md)  
**다음 단계:** [04-validation-error-envelope.md](./04-validation-error-envelope.md)

### Task 01: candle route 테스트 작성

**Files:**
- Create: `apps/backend/tests/test_candles_route.py`
- Create: `apps/backend/src/upbit_dashboard/api/routes/candles.py`
- Modify: `apps/backend/src/upbit_dashboard/api/router.py`

- [ ] **Step 1: 실패하는 route 테스트 작성**

`apps/backend/tests/test_candles_route.py`를 만든다.

```python
from fastapi.testclient import TestClient

from upbit_dashboard.main import create_app
from upbit_dashboard.upbit.rest import UpbitCandleResponse


class FakeRestClient:
    def __init__(self) -> None:
        self.calls = []

    async def list_candles(self, *, path: str, market: str, count: int, to: str | None):
        self.calls.append({"path": path, "market": market, "count": count, "to": to})
        return [
            UpbitCandleResponse(
                market="KRW-BTC",
                candle_date_time_utc="2026-06-01T00:01:00",
                candle_date_time_kst="2026-06-01T09:01:00",
                opening_price=101.0,
                high_price=111.0,
                low_price=91.0,
                trade_price=106.0,
                candle_acc_trade_volume=2.0,
                candle_acc_trade_price=202000.0,
            ),
            UpbitCandleResponse(
                market="KRW-BTC",
                candle_date_time_utc="2026-06-01T00:00:00",
                candle_date_time_kst="2026-06-01T09:00:00",
                opening_price=100.0,
                high_price=110.0,
                low_price=90.0,
                trade_price=105.0,
                candle_acc_trade_volume=1.5,
                candle_acc_trade_price=150000.0,
            ),
        ]


def test_candles_route_maps_query_and_returns_old_to_new(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")
    app = create_app()
    fake_client = FakeRestClient()
    app.state.upbit_rest_client = fake_client

    with TestClient(app) as client:
        response = client.get(
            "/api/candles",
            params={
                "market": "KRW-BTC",
                "unit": "1h",
                "count": "2",
                "to": "2026-06-01T00:00:00Z",
            },
        )

    assert response.status_code == 200
    assert fake_client.calls == [
        {
            "path": "/v1/candles/minutes/60",
            "market": "KRW-BTC",
            "count": 2,
            "to": "2026-06-01T00:00:00Z",
        }
    ]
    body = response.json()
    assert body["type"] == "candles:list"
    assert body["data"]["market"] == "KRW-BTC"
    assert body["data"]["candleUnit"] == "1h"
    assert [candle["candleDateTimeUtc"] for candle in body["data"]["candles"]] == [
        "2026-06-01T00:00:00",
        "2026-06-01T00:01:00",
    ]


def test_candles_route_uses_default_count_200(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")
    app = create_app()
    fake_client = FakeRestClient()
    app.state.upbit_rest_client = fake_client

    with TestClient(app) as client:
        response = client.get("/api/candles?market=KRW-BTC&unit=1m")

    assert response.status_code == 200
    assert fake_client.calls[0]["count"] == 200


def test_candles_route_rejects_count_above_200(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")

    with TestClient(create_app()) as client:
        response = client.get("/api/candles?market=KRW-BTC&unit=1m&count=201")

    assert response.status_code == 422


def test_candles_route_rejects_non_krw_market(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")

    with TestClient(create_app()) as client:
        response = client.get("/api/candles?market=USDT-BTC&unit=1m")

    assert response.status_code == 400
    assert response.json()["type"] == "error"
    assert response.json()["data"]["code"] == "BAD_REQUEST"
```

- [ ] **Step 2: 테스트 실패 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_candles_route.py -q
```

Expected:

```text
404 Not Found
```

### Task 02: candle route 구현

**Files:**
- Create: `apps/backend/src/upbit_dashboard/api/routes/candles.py`
- Modify: `apps/backend/src/upbit_dashboard/api/router.py`
- Modify: `apps/backend/src/upbit_dashboard/main.py`

- [ ] **Step 1: `main.py`에 rest client state 보관**

`create_app()`에서 `UpbitRestClient` instance를 변수로 만들고 app state에 보관한다.

```python
upbit_rest_client = UpbitRestClient(http_client=http_client)
app.state.upbit_rest_client = upbit_rest_client
app.state.market_catalogue = MarketCatalogueService(
    client=upbit_rest_client,
    ttl_seconds=settings.market_catalogue_ttl_seconds,
)
```

- [ ] **Step 2: candle route 작성**

`apps/backend/src/upbit_dashboard/api/routes/candles.py`를 만든다.

```python
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Query, Request

from upbit_dashboard.api.errors import DashboardApiError
from upbit_dashboard.contracts.errors import RestErrorCode
from upbit_dashboard.contracts.quotation import Candle, CandleUnit
from upbit_dashboard.contracts.rest import CandlesListData, CandlesListResponse
from upbit_dashboard.market.catalogue import assert_krw_market
from upbit_dashboard.upbit.rest import (
    UpbitCandleResponse,
    UpbitRestError,
    build_candle_path,
    map_upbit_rest_error,
)

router = APIRouter()


def map_upbit_candle(raw: UpbitCandleResponse) -> Candle:
    return Candle(
        candle_date_time_utc=raw.candle_date_time_utc,
        candle_date_time_kst=raw.candle_date_time_kst,
        opening_price=raw.opening_price,
        high_price=raw.high_price,
        low_price=raw.low_price,
        trade_price=raw.trade_price,
        candle_acc_trade_volume=raw.candle_acc_trade_volume,
        candle_acc_trade_price=raw.candle_acc_trade_price,
    )


def normalize_candle_market(raw_market: str) -> str:
    try:
        return assert_krw_market(raw_market).as_upbit_code()
    except ValueError as exc:
        raise DashboardApiError(
            code=RestErrorCode.BAD_REQUEST,
            message=str(exc),
            details={"market": raw_market},
            status_code=400,
        ) from exc


@router.get("/api/candles", response_model=CandlesListResponse)
async def get_candles(
    request: Request,
    market: str,
    unit: CandleUnit,
    count: Annotated[int, Query(ge=1, le=200)] = 200,
    to: str | None = None,
) -> CandlesListResponse:
    normalized_market = normalize_candle_market(market)
    path = build_candle_path(unit.value)

    try:
        raw_candles = await request.app.state.upbit_rest_client.list_candles(
            path=path,
            market=normalized_market,
            count=count,
            to=to,
        )
    except UpbitRestError as exc:
        raise map_upbit_rest_error(exc) from exc

    candles = sorted(
        (map_upbit_candle(raw_candle) for raw_candle in raw_candles),
        key=lambda candle: candle.candle_date_time_utc,
    )

    return CandlesListResponse(
        timestamp=datetime.now(timezone.utc),
        data=CandlesListData(
            market=normalized_market,
            candle_unit=unit,
            candles=candles,
        ),
    )
```

- [ ] **Step 3: router 등록**

`apps/backend/src/upbit_dashboard/api/router.py`를 다음 형태로 수정한다.

```python
from fastapi import APIRouter

from upbit_dashboard.api.routes import candles, health, markets, snapshot

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(markets.router)
api_router.include_router(snapshot.router)
api_router.include_router(candles.router)
```

- [ ] **Step 4: candle route 테스트 통과 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_candles_route.py -q
```

Expected:

```text
4 passed
```

- [ ] **Step 5: 관련 backend route 테스트 실행**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_candles_route.py apps/backend/tests/test_markets_route.py apps/backend/tests/test_snapshot.py -q
```

Expected:

```text
passed
```

- [ ] **Step 6: 단계 커밋**

Run:

```bash
rtk proxy git add apps/backend/src/upbit_dashboard/api/routes/candles.py apps/backend/src/upbit_dashboard/api/router.py apps/backend/src/upbit_dashboard/main.py apps/backend/tests/test_candles_route.py
rtk proxy git commit -m "feat: expose candle history endpoint"
```

Expected:

```text
커밋 생성
```
