# 04 Smoke Command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** FastAPI 서버 없이 Upbit REST/WS 연결을 확인하는 smoke command를 추가한다.

**Architecture:** smoke command는 `upbit_dashboard.tools` 아래에 둔다. REST 접근성은 Upbit market endpoint 응답 형태를 확인하고, WebSocket은 `stream_tickers()`를 사용해 Phase 2 Market 두 개를 각각 최소 1회 수신하면 성공한다.

**Tech Stack:** Python 3.12, httpx, asyncio, pytest, RTK.

---

**순서:** 04 / 06
**이전 단계:** [03-stream-runner.md](./03-stream-runner.md)
**다음 단계:** [05-fastapi-lifespan.md](./05-fastapi-lifespan.md)

### Task 04: Upbit 연결 smoke command 추가

**Files:**
- Create: `apps/backend/src/upbit_dashboard/tools/__init__.py`
- Create: `apps/backend/src/upbit_dashboard/tools/smoke_upbit_connection.py`
- Create: `apps/backend/tests/test_upbit_smoke.py`

- [ ] **Step 1: 실패하는 smoke helper 테스트 작성**

`apps/backend/tests/test_upbit_smoke.py`를 만든다.

```python
import pytest

from upbit_dashboard.tools.smoke_upbit_connection import validate_market_response


def test_validate_market_response_returns_market_count() -> None:
    data = [
        {"market": "KRW-BTC", "korean_name": "비트코인", "english_name": "Bitcoin"},
        {"market": "KRW-ETH", "korean_name": "이더리움", "english_name": "Ethereum"},
    ]

    assert validate_market_response(data) == 2


def test_validate_market_response_rejects_non_list() -> None:
    with pytest.raises(RuntimeError, match="list"):
        validate_market_response({"market": "KRW-BTC"})


def test_validate_market_response_rejects_items_without_market() -> None:
    with pytest.raises(RuntimeError, match="market"):
        validate_market_response([{"korean_name": "비트코인"}])
```

- [ ] **Step 2: 테스트 실패 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_upbit_smoke.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'upbit_dashboard.tools'
```

- [ ] **Step 3: tools 패키지와 smoke command 구현**

`apps/backend/src/upbit_dashboard/tools/__init__.py`를 만든다.

```python
"""Local command-line tools for the Upbit dashboard backend."""
```

`apps/backend/src/upbit_dashboard/tools/smoke_upbit_connection.py`를 만든다.

```python
from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from upbit_dashboard.contracts.quotation import TickerData
from upbit_dashboard.upbit.client import stream_tickers
from upbit_dashboard.upbit.settings import (
    DEFAULT_TICKER_MARKETS,
    DEFAULT_UPBIT_REST_MARKETS_URL,
    SMOKE_TIMEOUT_SECONDS,
)

logger = logging.getLogger(__name__)


def validate_market_response(data: Any) -> int:
    if not isinstance(data, list):
        raise RuntimeError("Upbit REST market response must be a list.")
    for item in data:
        if not isinstance(item, dict) or not isinstance(item.get("market"), str):
            raise RuntimeError("Upbit REST market response items must include market.")
    return len(data)


async def check_rest_market_endpoint(url: str = DEFAULT_UPBIT_REST_MARKETS_URL) -> int:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        count = validate_market_response(response.json())
        logger.info("REST market check ok count=%s", count)
        return count


async def collect_required_tickers(
    markets: tuple[str, ...] = DEFAULT_TICKER_MARKETS,
    timeout_seconds: float = SMOKE_TIMEOUT_SECONDS,
) -> dict[str, TickerData]:
    required = set(markets)
    received: dict[str, TickerData] = {}

    try:
        async with asyncio.timeout(timeout_seconds):
            async for ticker in stream_tickers(markets=markets):
                logger.info(
                    "ticker received market=%s tradePrice=%s streamType=%s",
                    ticker.market,
                    ticker.trade_price,
                    ticker.stream_type.value,
                )
                if ticker.market in required:
                    received[ticker.market] = ticker
                if required.issubset(received):
                    return received
    except TimeoutError as exc:
        missing = ",".join(sorted(required.difference(received)))
        raise TimeoutError(f"Missing ticker markets before timeout: {missing}") from exc

    missing = ",".join(sorted(required.difference(received)))
    raise RuntimeError(f"Ticker stream ended before required markets arrived: {missing}")


async def main_async() -> None:
    await check_rest_market_endpoint()
    received = await collect_required_tickers()
    logger.info("smoke ok markets=%s", ",".join(sorted(received)))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        asyncio.run(main_async())
    except Exception:
        logger.exception("smoke failed")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: smoke helper 테스트 통과 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_upbit_smoke.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 5: 전체 backend 테스트 통과 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest -q
```

Expected:

```text
전체 backend 테스트 통과
```

- [ ] **Step 6: 단계 커밋**

Run:

```bash
rtk proxy git add apps/backend/src/upbit_dashboard/tools apps/backend/tests/test_upbit_smoke.py
rtk proxy git commit -m "feat: add upbit connection smoke command"
```

Expected:

```text
커밋 생성
```
