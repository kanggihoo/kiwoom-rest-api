# 02 Market Catalogue Route Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** FastAPI `GET /api/markets`를 추가해 KRW Market 메타데이터를 10분 cache와 stale-on-error 정책으로 반환한다.

**Architecture:** `MarketCatalogueService`는 Upbit REST adapter에서 받은 raw Market 목록을 `MarketSummary`로 변환하고 process-memory cache를 관리한다. Service는 `asyncio.Lock`으로 refresh 중복만 막고, Next.js BFF cache는 이 단계에서 다루지 않는다.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, httpx MockTransport, pytest, RTK.

---

**순서:** 02 / 07  
**이전 단계:** [01-upbit-rest-adapter.md](./01-upbit-rest-adapter.md)  
**다음 단계:** [03-candles-route.md](./03-candles-route.md)

### Task 01: Market catalogue 변환/cache 테스트 작성

**Files:**
- Modify: `apps/backend/tests/test_market_catalogue.py`
- Modify: `apps/backend/src/upbit_dashboard/market/catalogue.py`

- [ ] **Step 1: 실패하는 service 테스트 추가**

`apps/backend/tests/test_market_catalogue.py` 끝에 다음 테스트를 추가한다.

```python
from datetime import datetime, timedelta, timezone

import anyio

from upbit_dashboard.contracts.rest import MarketSummary
from upbit_dashboard.market.catalogue import MarketCatalogueService, map_upbit_market_summary
from upbit_dashboard.upbit.rest import UpbitMarketResponse, UpbitRestError


class FakeMarketClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    async def list_markets(self):
        self.calls += 1
        result = self.responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


def test_map_upbit_market_summary_filters_and_maps_krw_market() -> None:
    summary = map_upbit_market_summary(
        UpbitMarketResponse(
            market="KRW-BTC",
            korean_name="비트코인",
            english_name="Bitcoin",
        )
    )

    assert summary == MarketSummary(
        market="KRW-BTC",
        korean_name="비트코인",
        english_name="Bitcoin",
        quote_currency="KRW",
        base_currency="BTC",
    )


def test_market_catalogue_service_filters_krw_and_caches_fresh_result() -> None:
    async def run_test() -> None:
        client = FakeMarketClient(
            [
                [
                    UpbitMarketResponse(market="KRW-BTC", korean_name="비트코인", english_name="Bitcoin"),
                    UpbitMarketResponse(market="USDT-BTC", korean_name="비트코인", english_name="Bitcoin"),
                ]
            ]
        )
        service = MarketCatalogueService(client=client, ttl_seconds=600)
        now = datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc)

        first = await service.list_krw_markets(now=now)
        second = await service.list_krw_markets(now=now + timedelta(seconds=10))

        assert [market.market for market in first] == ["KRW-BTC"]
        assert second == first
        assert client.calls == 1

    anyio.run(run_test)


def test_market_catalogue_service_refreshes_expired_cache() -> None:
    async def run_test() -> None:
        client = FakeMarketClient(
            [
                [UpbitMarketResponse(market="KRW-BTC", korean_name="비트코인", english_name="Bitcoin")],
                [UpbitMarketResponse(market="KRW-ETH", korean_name="이더리움", english_name="Ethereum")],
            ]
        )
        service = MarketCatalogueService(client=client, ttl_seconds=600)
        now = datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc)

        await service.list_krw_markets(now=now)
        refreshed = await service.list_krw_markets(now=now + timedelta(seconds=601))

        assert [market.market for market in refreshed] == ["KRW-ETH"]
        assert client.calls == 2

    anyio.run(run_test)


def test_market_catalogue_service_returns_stale_on_refresh_failure() -> None:
    async def run_test() -> None:
        client = FakeMarketClient(
            [
                [UpbitMarketResponse(market="KRW-BTC", korean_name="비트코인", english_name="Bitcoin")],
                UpbitRestError(status_code=502, message="Upbit failed"),
            ]
        )
        service = MarketCatalogueService(client=client, ttl_seconds=600)
        now = datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc)

        await service.list_krw_markets(now=now)
        stale = await service.list_krw_markets(now=now + timedelta(seconds=601))

        assert [market.market for market in stale] == ["KRW-BTC"]
        assert client.calls == 2

    anyio.run(run_test)
```

- [ ] **Step 2: 테스트 실패 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_market_catalogue.py -q
```

Expected:

```text
ImportError: cannot import name 'MarketCatalogueService'
```

### Task 02: Market catalogue service 구현

**Files:**
- Modify: `apps/backend/src/upbit_dashboard/market/catalogue.py`

- [ ] **Step 1: service와 mapper 추가**

`apps/backend/src/upbit_dashboard/market/catalogue.py`에 기존 함수 아래로 다음 코드를 추가한다.

```python
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Protocol

from upbit_dashboard.contracts.rest import MarketSummary
from upbit_dashboard.upbit.rest import UpbitMarketResponse


class MarketClient(Protocol):
    async def list_markets(self) -> list[UpbitMarketResponse]:
        ...


def map_upbit_market_summary(market: UpbitMarketResponse) -> MarketSummary:
    parsed = assert_krw_market(market.market)
    return MarketSummary(
        market=parsed.as_upbit_code(),
        korean_name=market.korean_name,
        english_name=market.english_name,
        quote_currency=parsed.quote_currency,
        base_currency=parsed.base_currency,
    )


class MarketCatalogueService:
    def __init__(self, *, client: MarketClient, ttl_seconds: int) -> None:
        self._client = client
        self._ttl = timedelta(seconds=ttl_seconds)
        self._markets: tuple[MarketSummary, ...] | None = None
        self._fetched_at: datetime | None = None
        self._refresh_lock = asyncio.Lock()

    async def list_krw_markets(self, now: datetime | None = None) -> tuple[MarketSummary, ...]:
        current_time = now or datetime.now(timezone.utc)
        fresh = self._fresh(current_time)
        if fresh is not None:
            return fresh

        async with self._refresh_lock:
            current_time = now or datetime.now(timezone.utc)
            fresh = self._fresh(current_time)
            if fresh is not None:
                return fresh

            try:
                raw_markets = await self._client.list_markets()
            except Exception:
                if self._markets is not None:
                    return self._markets
                raise

            krw_markets = tuple(
                map_upbit_market_summary(raw_market)
                for raw_market in raw_markets
                if is_krw_market(raw_market.market)
            )
            self._markets = krw_markets
            self._fetched_at = current_time
            return krw_markets

    def _fresh(self, now: datetime) -> tuple[MarketSummary, ...] | None:
        if self._markets is None or self._fetched_at is None:
            return None
        if now - self._fetched_at > self._ttl:
            return None
        return self._markets
```

- [ ] **Step 2: import 정리**

같은 파일 상단 import가 중복되지 않게 다음 형태가 되도록 정리한다.

```python
import asyncio
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol
```

- [ ] **Step 3: service 테스트 통과 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_market_catalogue.py -q
```

Expected:

```text
기존 테스트와 신규 테스트 모두 passed
```

### Task 03: `/api/markets` route 테스트 작성

**Files:**
- Create: `apps/backend/tests/test_markets_route.py`
- Create: `apps/backend/src/upbit_dashboard/api/routes/markets.py`
- Modify: `apps/backend/src/upbit_dashboard/api/router.py`
- Modify: `apps/backend/src/upbit_dashboard/main.py`
- Modify: `apps/backend/src/upbit_dashboard/settings.py`
- Modify: `apps/backend/tests/conftest.py`

- [ ] **Step 1: route 테스트 작성**

`apps/backend/tests/test_markets_route.py`를 만든다.

```python
from fastapi.testclient import TestClient

from upbit_dashboard.contracts.rest import MarketSummary
from upbit_dashboard.main import create_app


class FakeMarketCatalogue:
    async def list_krw_markets(self):
        return (
            MarketSummary(
                market="KRW-BTC",
                korean_name="비트코인",
                english_name="Bitcoin",
                quote_currency="KRW",
                base_currency="BTC",
            ),
        )


def test_markets_route_returns_market_metadata(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")
    app = create_app()
    app.state.market_catalogue = FakeMarketCatalogue()

    with TestClient(app) as client:
        response = client.get("/api/markets")

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "markets:list"
    assert body["data"]["markets"] == [
        {
            "market": "KRW-BTC",
            "koreanName": "비트코인",
            "englishName": "Bitcoin",
            "quoteCurrency": "KRW",
            "baseCurrency": "BTC",
        }
    ]
```

- [ ] **Step 2: 테스트 실패 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_markets_route.py -q
```

Expected:

```text
404 Not Found
```

### Task 04: settings와 route 구현

**Files:**
- Create: `apps/backend/src/upbit_dashboard/api/routes/markets.py`
- Modify: `apps/backend/src/upbit_dashboard/api/router.py`
- Modify: `apps/backend/src/upbit_dashboard/main.py`
- Modify: `apps/backend/src/upbit_dashboard/settings.py`
- Modify: `apps/backend/tests/conftest.py`

- [ ] **Step 1: settings에 cache TTL과 REST base URL 추가**

`apps/backend/src/upbit_dashboard/settings.py`에 다음 상수와 필드를 추가한다.

```python
DEFAULT_UPBIT_REST_BASE_URL = "https://api.upbit.com"
DEFAULT_MARKET_CATALOGUE_TTL_SECONDS = 600
```

`BackendSettings`에 다음 필드를 추가한다.

```python
upbit_rest_base_url: str = Field(
    DEFAULT_UPBIT_REST_BASE_URL,
    validation_alias="UPBIT_REST_BASE_URL",
)
market_catalogue_ttl_seconds: int = Field(
    DEFAULT_MARKET_CATALOGUE_TTL_SECONDS,
    gt=0,
    validation_alias="MARKET_CATALOGUE_TTL_SECONDS",
)
```

기존 `_FLOAT_DEFAULTS` 옆에 정수 기본값 mapping을 추가한다.

```python
_INT_DEFAULTS = {
    "market_catalogue_ttl_seconds": DEFAULT_MARKET_CATALOGUE_TTL_SECONDS,
}
```

`BackendSettings`에 validator를 추가한다.

```python
@field_validator("market_catalogue_ttl_seconds", mode="before")
@classmethod
def validate_optional_positive_int(
    cls,
    value: object,
    info: ValidationInfo,
) -> object:
    if isinstance(value, str) and value.strip() == "":
        return _INT_DEFAULTS[info.field_name]
    return value
```

`apps/backend/tests/conftest.py`의 `SETTING_ENV_NAMES`에 추가한다.

```python
"UPBIT_REST_BASE_URL",
"MARKET_CATALOGUE_TTL_SECONDS",
```

- [ ] **Step 2: `main.py`에서 service 생성**

`apps/backend/src/upbit_dashboard/main.py`에 import를 추가한다.

```python
import httpx

from upbit_dashboard.market.catalogue import MarketCatalogueService
from upbit_dashboard.upbit.rest import UpbitRestClient
```

`create_app()`에서 `app.state.market_state = MarketState()` 아래에 추가한다.

```python
settings = get_settings()
http_client = httpx.AsyncClient(base_url=settings.upbit_rest_base_url, timeout=5.0)
app.state.upbit_rest_http_client = http_client
app.state.market_catalogue = MarketCatalogueService(
    client=UpbitRestClient(http_client=http_client),
    ttl_seconds=settings.market_catalogue_ttl_seconds,
)
```

lifespan cleanup에 HTTP client 종료를 추가한다.

```python
http_client = getattr(app.state, "upbit_rest_http_client", None)
if http_client is not None:
    await http_client.aclose()
```

- [ ] **Step 3: `/api/markets` route 구현**

`apps/backend/src/upbit_dashboard/api/routes/markets.py`를 만든다.

```python
from datetime import datetime, timezone

from fastapi import APIRouter, Request

from upbit_dashboard.contracts.rest import MarketsListData, MarketsListResponse
from upbit_dashboard.upbit.rest import UpbitRestError, map_upbit_rest_error

router = APIRouter()


@router.get("/api/markets", response_model=MarketsListResponse)
async def get_markets(request: Request) -> MarketsListResponse:
    try:
        markets = await request.app.state.market_catalogue.list_krw_markets()
    except UpbitRestError as exc:
        raise map_upbit_rest_error(exc) from exc

    return MarketsListResponse(
        timestamp=datetime.now(timezone.utc),
        data=MarketsListData(markets=list(markets)),
    )
```

`apps/backend/src/upbit_dashboard/api/router.py`에 route를 등록한다.

```python
from fastapi import APIRouter

from upbit_dashboard.api.routes import health, markets, snapshot

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(markets.router)
api_router.include_router(snapshot.router)
```

- [ ] **Step 4: route와 settings 테스트 실행**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_markets_route.py apps/backend/tests/test_market_catalogue.py apps/backend/tests/test_settings.py -q
```

Expected:

```text
passed
```

- [ ] **Step 5: 단계 커밋**

Run:

```bash
rtk proxy git add apps/backend/src/upbit_dashboard/market/catalogue.py apps/backend/src/upbit_dashboard/api/routes/markets.py apps/backend/src/upbit_dashboard/api/router.py apps/backend/src/upbit_dashboard/main.py apps/backend/src/upbit_dashboard/settings.py apps/backend/tests/conftest.py apps/backend/tests/test_market_catalogue.py apps/backend/tests/test_markets_route.py apps/backend/tests/test_settings.py
rtk proxy git commit -m "feat: expose krw market catalogue"
```

Expected:

```text
커밋 생성
```
