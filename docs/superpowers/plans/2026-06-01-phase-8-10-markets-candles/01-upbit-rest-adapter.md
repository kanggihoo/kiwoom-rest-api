# 01 Upbit REST Adapter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upbit Quotation REST API를 호출하는 backend adapter와 공통 error mapping을 추가한다.

**Architecture:** 새 `upbit_dashboard.upbit.rest` module은 `httpx.AsyncClient`를 사용해 Upbit REST JSON을 가져오고, raw response model을 Pydantic으로 검증한 뒤 route/service에서 사용할 typed 객체를 반환한다. Upbit HTTP status, timeout, network error는 `UpbitRestError`로 통일하고 route/service는 이를 `DashboardApiError`로 변환한다.

**Tech Stack:** Python 3.12, httpx, Pydantic v2, pytest, anyio, uv, RTK.

---

**순서:** 01 / 07  
**이전 단계:** 없음  
**다음 단계:** [02-market-catalogue-route.md](./02-market-catalogue-route.md)

### Task 01: `httpx` runtime dependency 이동

**Files:**
- Modify: `apps/backend/pyproject.toml`

- [ ] **Step 1: dependency 상태 확인**

Run:

```bash
rtk proxy sed -n '1,80p' apps/backend/pyproject.toml
```

Expected:

```text
httpx가 dependency-groups.dev에만 있음
```

- [ ] **Step 2: `httpx`를 runtime dependencies로 이동**

`apps/backend/pyproject.toml`을 다음 구조로 수정한다.

```toml
[project]
name = "upbit-dashboard"
version = "0.1.0"
description = "FastAPI backend for the Upbit dashboard"
authors = [
    { name = "kkh", email = "11kkh19999@gmail.com" }
]
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.136.3",
    "httpx>=0.28.1",
    "pydantic>=2.13.4",
    "pydantic-settings>=2.14.1",
    "rich>=14.0.0",
    "uvicorn[standard]>=0.48.0",
    "websockets>=16.0",
]

[build-system]
requires = ["uv_build>=0.8.13,<0.9.0"]
build-backend = "uv_build"

[dependency-groups]
dev = [
    "pytest>=9.0.3",
]
```

- [ ] **Step 3: lockfile 갱신 확인**

Run:

```bash
rtk proxy uv lock --project apps/backend
```

Expected:

```text
uv.lock 갱신 또는 이미 최신 상태
```

### Task 02: Upbit REST adapter 테스트 작성

**Files:**
- Create: `apps/backend/tests/test_upbit_rest.py`
- Create: `apps/backend/src/upbit_dashboard/upbit/rest.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`apps/backend/tests/test_upbit_rest.py`를 만든다.

```python
from __future__ import annotations

import anyio
import httpx
import pytest

from upbit_dashboard.upbit.rest import (
    UpbitRestClient,
    UpbitRestError,
    build_candle_path,
    map_upbit_rest_error,
)


def test_list_markets_returns_raw_market_models() -> None:
    async def run_test() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/market/all"
            assert request.url.params["is_details"] == "false"
            return httpx.Response(
                200,
                json=[
                    {
                        "market": "KRW-BTC",
                        "korean_name": "비트코인",
                        "english_name": "Bitcoin",
                    }
                ],
            )

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="https://api.upbit.com") as http_client:
            client = UpbitRestClient(http_client=http_client)
            markets = await client.list_markets()

        assert markets[0].market == "KRW-BTC"
        assert markets[0].korean_name == "비트코인"
        assert markets[0].english_name == "Bitcoin"

    anyio.run(run_test)


def test_list_candles_returns_raw_candle_models() -> None:
    async def run_test() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/candles/minutes/1"
            assert request.url.params["market"] == "KRW-BTC"
            assert request.url.params["count"] == "2"
            return httpx.Response(
                200,
                json=[
                    {
                        "market": "KRW-BTC",
                        "candle_date_time_utc": "2026-06-01T00:01:00",
                        "candle_date_time_kst": "2026-06-01T09:01:00",
                        "opening_price": 100.0,
                        "high_price": 110.0,
                        "low_price": 90.0,
                        "trade_price": 105.0,
                        "candle_acc_trade_volume": 1.5,
                        "candle_acc_trade_price": 150000.0,
                    }
                ],
            )

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="https://api.upbit.com") as http_client:
            client = UpbitRestClient(http_client=http_client)
            candles = await client.list_candles(path="/v1/candles/minutes/1", market="KRW-BTC", count=2, to=None)

        assert candles[0].market == "KRW-BTC"
        assert candles[0].trade_price == 105.0

    anyio.run(run_test)


def test_build_candle_path_maps_supported_units() -> None:
    assert build_candle_path("1m") == "/v1/candles/minutes/1"
    assert build_candle_path("5m") == "/v1/candles/minutes/5"
    assert build_candle_path("15m") == "/v1/candles/minutes/15"
    assert build_candle_path("30m") == "/v1/candles/minutes/30"
    assert build_candle_path("1h") == "/v1/candles/minutes/60"
    assert build_candle_path("1d") == "/v1/candles/days"
    assert build_candle_path("1w") == "/v1/candles/weeks"


def test_upbit_error_response_raises_typed_error() -> None:
    async def run_test() -> None:
        def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(
                429,
                headers={"Remaining-Req": "group=candle; min=1800; sec=0"},
                json={"error": {"name": 429, "message": "Too many requests"}},
            )

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="https://api.upbit.com") as http_client:
            client = UpbitRestClient(http_client=http_client)
            with pytest.raises(UpbitRestError) as exc_info:
                await client.list_markets()

        assert exc_info.value.status_code == 429
        assert exc_info.value.remaining_req == "group=candle; min=1800; sec=0"
        assert exc_info.value.error_name == "429"

    anyio.run(run_test)


def test_map_upbit_rest_error_maps_rate_limit_status() -> None:
    api_error = map_upbit_rest_error(
        UpbitRestError(
            status_code=429,
            message="Too many requests",
            error_name="429",
            remaining_req="group=candle; min=1800; sec=0",
        )
    )

    assert api_error.code == "RATE_LIMITED"
    assert api_error.status_code == 429
    assert api_error.details == {
        "upbitStatus": 429,
        "upbitErrorName": "429",
        "remainingReq": "group=candle; min=1800; sec=0",
    }
```

- [ ] **Step 2: 테스트 실패 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_upbit_rest.py -q
```

Expected:

```text
ModuleNotFoundError 또는 ImportError
```

### Task 03: Upbit REST adapter 구현

**Files:**
- Create: `apps/backend/src/upbit_dashboard/upbit/rest.py`

- [ ] **Step 1: adapter module 작성**

`apps/backend/src/upbit_dashboard/upbit/rest.py`를 만든다.

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx
from pydantic import BaseModel, Field, TypeAdapter

from upbit_dashboard.api.errors import DashboardApiError
from upbit_dashboard.contracts.errors import RestErrorCode


class UpbitMarketResponse(BaseModel):
    market: str = Field(description="Upbit Market code.")
    korean_name: str = Field(description="Korean Market name.")
    english_name: str = Field(description="English Market name.")


class UpbitCandleResponse(BaseModel):
    market: str = Field(description="Upbit Market code.")
    candle_date_time_utc: str = Field(description="Candle time in UTC.")
    candle_date_time_kst: str = Field(description="Candle time in KST.")
    opening_price: float
    high_price: float
    low_price: float
    trade_price: float
    candle_acc_trade_volume: float
    candle_acc_trade_price: float


@dataclass(frozen=True)
class UpbitRestError(Exception):
    status_code: int | None
    message: str
    error_name: str | None = None
    remaining_req: str | None = None


MARKET_LIST_PATH = "/v1/market/all"

_MARKET_LIST_ADAPTER = TypeAdapter(list[UpbitMarketResponse])
_CANDLE_LIST_ADAPTER = TypeAdapter(list[UpbitCandleResponse])


def build_candle_path(unit: str) -> str:
    paths = {
        "1m": "/v1/candles/minutes/1",
        "5m": "/v1/candles/minutes/5",
        "15m": "/v1/candles/minutes/15",
        "30m": "/v1/candles/minutes/30",
        "1h": "/v1/candles/minutes/60",
        "1d": "/v1/candles/days",
        "1w": "/v1/candles/weeks",
    }
    return paths[unit]


class UpbitRestClient:
    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self._http_client = http_client

    async def list_markets(self) -> list[UpbitMarketResponse]:
        response = await self._request("GET", MARKET_LIST_PATH, params={"is_details": "false"})
        return _MARKET_LIST_ADAPTER.validate_python(response.json())

    async def list_candles(
        self,
        *,
        path: str,
        market: str,
        count: int,
        to: str | None,
    ) -> list[UpbitCandleResponse]:
        params: dict[str, str | int] = {"market": market, "count": count}
        if to is not None:
            params["to"] = to
        response = await self._request("GET", path, params=params)
        return _CANDLE_LIST_ADAPTER.validate_python(response.json())

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any],
    ) -> httpx.Response:
        try:
            response = await self._http_client.request(method, path, params=params)
        except httpx.TimeoutException as exc:
            raise UpbitRestError(status_code=None, message="Upbit REST request timed out.") from exc
        except httpx.HTTPError as exc:
            raise UpbitRestError(status_code=None, message="Upbit REST request failed.") from exc

        if response.is_success:
            return response

        error_name: str | None = None
        message = f"Upbit REST responded with HTTP {response.status_code}."
        try:
            body = response.json()
        except ValueError:
            body = None
        if isinstance(body, dict) and isinstance(body.get("error"), dict):
            error = body["error"]
            raw_name = error.get("name")
            raw_message = error.get("message")
            error_name = str(raw_name) if raw_name is not None else None
            message = raw_message if isinstance(raw_message, str) else message

        raise UpbitRestError(
            status_code=response.status_code,
            message=message,
            error_name=error_name,
            remaining_req=response.headers.get("Remaining-Req"),
        )


def map_upbit_rest_error(error: UpbitRestError) -> DashboardApiError:
    status_code = error.status_code
    details = {
        "upbitStatus": status_code,
        "upbitErrorName": error.error_name,
        "remainingReq": error.remaining_req,
    }

    if status_code == 418:
        return DashboardApiError(
            code=RestErrorCode.TEMPORARILY_BLOCKED,
            message=error.message,
            details=details,
            status_code=418,
        )
    if status_code == 429:
        return DashboardApiError(
            code=RestErrorCode.RATE_LIMITED,
            message=error.message,
            details=details,
            status_code=429,
        )
    if status_code == 400:
        return DashboardApiError(
            code=RestErrorCode.UPBIT_BAD_REQUEST,
            message=error.message,
            details=details,
            status_code=502,
        )
    if status_code is None:
        return DashboardApiError(
            code=RestErrorCode.UPBIT_TIMEOUT if "timed out" in error.message else RestErrorCode.UPBIT_ERROR,
            message=error.message,
            details=details,
        )
    return DashboardApiError(
        code=RestErrorCode.UPBIT_ERROR,
        message=error.message,
        details=details,
    )
```

- [ ] **Step 2: adapter 테스트 통과 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_upbit_rest.py -q
```

Expected:

```text
5 passed
```

- [ ] **Step 3: 단계 커밋**

Run:

```bash
rtk proxy git add apps/backend/pyproject.toml apps/backend/uv.lock apps/backend/src/upbit_dashboard/upbit/rest.py apps/backend/tests/test_upbit_rest.py
rtk proxy git commit -m "feat: add upbit quotation rest adapter"
```

Expected:

```text
커밋 생성
```
