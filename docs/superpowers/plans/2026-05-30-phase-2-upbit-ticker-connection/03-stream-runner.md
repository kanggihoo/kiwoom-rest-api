# 03 Stream Runner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upbit WebSocket 단일 stream client와 reconnect/backoff runner를 추가한다.

**Architecture:** `client.py`는 단일 WebSocket 연결에서 구독 메시지를 보내고 ticker를 yield한다. `runner.py`는 연결 반복, backoff, shutdown signal, ticker handler 호출을 담당한다. Phase 2의 기본 handler는 로그 출력이고, `MarketState` 저장은 이 계획에 포함하지 않는다.

**Tech Stack:** Python 3.12, websockets, pytest, asyncio, RTK.

---

**순서:** 03 / 06
**이전 단계:** [02-payload-parsing.md](./02-payload-parsing.md)
**다음 단계:** [04-smoke-command.md](./04-smoke-command.md)

### Task 03: WebSocket stream과 reconnect runner 추가

**Files:**
- Modify: `apps/backend/src/upbit_dashboard/upbit/client.py`
- Create: `apps/backend/src/upbit_dashboard/upbit/runner.py`
- Create: `apps/backend/tests/test_upbit_runner.py`

- [ ] **Step 1: 실패하는 runner 단위 테스트 작성**

`apps/backend/tests/test_upbit_runner.py`를 만든다.

```python
from upbit_dashboard.upbit.runner import next_backoff


def test_next_backoff_doubles_until_maximum() -> None:
    assert next_backoff(current=1.0, maximum=30.0) == 2.0
    assert next_backoff(current=16.0, maximum=30.0) == 30.0
    assert next_backoff(current=30.0, maximum=30.0) == 30.0


def test_next_backoff_rejects_non_positive_values() -> None:
    try:
        next_backoff(current=0.0, maximum=30.0)
    except ValueError as exc:
        assert "current" in str(exc)
    else:
        raise AssertionError("next_backoff must reject non-positive current values")

    try:
        next_backoff(current=1.0, maximum=0.0)
    except ValueError as exc:
        assert "maximum" in str(exc)
    else:
        raise AssertionError("next_backoff must reject non-positive maximum values")
```

- [ ] **Step 2: 테스트 실패 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_upbit_runner.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'upbit_dashboard.upbit.runner'
```

- [ ] **Step 3: 단일 WebSocket stream client 구현**

`apps/backend/src/upbit_dashboard/upbit/client.py`의 import와 하단에 다음 코드를 추가한다.

```python
from collections.abc import AsyncIterator, Sequence
import json
import logging
from typing import Any

from websockets.asyncio.client import connect

from upbit_dashboard.contracts.mappers import map_upbit_ticker_message
from upbit_dashboard.contracts.quotation import TickerData
from upbit_dashboard.contracts.upbit import UpbitTickerMessage
from upbit_dashboard.upbit.settings import (
    DEFAULT_TICKER_MARKETS,
    DEFAULT_TICKET,
    DEFAULT_UPBIT_WS_ENDPOINT,
    DEFAULT_WS_FORMAT,
)

logger = logging.getLogger(__name__)
```

`client.py` 하단에 `stream_tickers`를 추가한다.

```python
async def stream_tickers(
    markets: Sequence[str] = DEFAULT_TICKER_MARKETS,
    endpoint: str = DEFAULT_UPBIT_WS_ENDPOINT,
) -> AsyncIterator[TickerData]:
    subscription = build_ticker_subscription(markets)
    async with connect(endpoint, ping_interval=20, ping_timeout=20) as websocket:
        await websocket.send(json.dumps(subscription))
        logger.info("Upbit WS connected endpoint=%s", endpoint)
        async for payload in websocket:
            try:
                yield parse_ticker_payload(payload)
            except UpbitWebSocketError:
                logger.exception("Upbit WS error payload received")
            except Exception:
                logger.exception("Upbit WS message validation failed")
```

`client.py` 최종 import 구성이 중복되면 중복 import를 제거한다. 파일 상단은 다음 형태가 되어야 한다.

```python
from collections.abc import AsyncIterator, Sequence
import json
import logging
from typing import Any

from websockets.asyncio.client import connect

from upbit_dashboard.contracts.mappers import map_upbit_ticker_message
from upbit_dashboard.contracts.quotation import TickerData
from upbit_dashboard.contracts.upbit import UpbitTickerMessage
from upbit_dashboard.upbit.settings import (
    DEFAULT_TICKER_MARKETS,
    DEFAULT_TICKET,
    DEFAULT_UPBIT_WS_ENDPOINT,
    DEFAULT_WS_FORMAT,
)
```

- [ ] **Step 4: reconnect/backoff runner 구현**

`apps/backend/src/upbit_dashboard/upbit/runner.py`를 만든다.

```python
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
import inspect
import logging

from upbit_dashboard.contracts.quotation import TickerData
from upbit_dashboard.upbit.client import stream_tickers
from upbit_dashboard.upbit.settings import (
    DEFAULT_TICKER_MARKETS,
    DEFAULT_UPBIT_WS_ENDPOINT,
    INITIAL_BACKOFF_SECONDS,
    MAX_BACKOFF_SECONDS,
)

logger = logging.getLogger(__name__)

TickerHandler = Callable[[TickerData], None | Awaitable[None]]


def next_backoff(current: float, maximum: float) -> float:
    if current <= 0:
        raise ValueError("current backoff must be positive")
    if maximum <= 0:
        raise ValueError("maximum backoff must be positive")
    return min(current * 2, maximum)


async def log_ticker(ticker: TickerData) -> None:
    logger.info(
        "Upbit ticker received market=%s tradePrice=%s streamType=%s",
        ticker.market,
        ticker.trade_price,
        ticker.stream_type.value,
    )


async def emit_ticker(handler: TickerHandler, ticker: TickerData) -> None:
    result = handler(ticker)
    if inspect.isawaitable(result):
        await result


async def _sleep_or_stop(stop_event: asyncio.Event | None, delay: float) -> None:
    if stop_event is None:
        await asyncio.sleep(delay)
        return
    try:
        await asyncio.wait_for(stop_event.wait(), timeout=delay)
    except TimeoutError:
        return


async def run_ticker_stream(
    markets: Sequence[str] = DEFAULT_TICKER_MARKETS,
    endpoint: str = DEFAULT_UPBIT_WS_ENDPOINT,
    on_ticker: TickerHandler = log_ticker,
    stop_event: asyncio.Event | None = None,
    initial_backoff: float = INITIAL_BACKOFF_SECONDS,
    max_backoff: float = MAX_BACKOFF_SECONDS,
) -> None:
    logger.info("Upbit ticker stream starting markets=%s", ",".join(markets))
    backoff = initial_backoff

    while stop_event is None or not stop_event.is_set():
        try:
            async for ticker in stream_tickers(markets=markets, endpoint=endpoint):
                backoff = initial_backoff
                await emit_ticker(on_ticker, ticker)
                if stop_event is not None and stop_event.is_set():
                    return
        except asyncio.CancelledError:
            raise
        except Exception:
            if stop_event is not None and stop_event.is_set():
                return
            logger.warning("Upbit WS disconnected; reconnecting in %.1fs", backoff, exc_info=True)
            await _sleep_or_stop(stop_event, backoff)
            backoff = next_backoff(backoff, max_backoff)
```

- [ ] **Step 5: runner 테스트 통과 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_upbit_runner.py apps/backend/tests/test_upbit_client.py -q
```

Expected:

```text
7 passed
```

- [ ] **Step 6: 단계 커밋**

Run:

```bash
rtk proxy git add apps/backend/src/upbit_dashboard/upbit/client.py apps/backend/src/upbit_dashboard/upbit/runner.py apps/backend/tests/test_upbit_runner.py
rtk proxy git commit -m "feat: add upbit ticker stream runner"
```

Expected:

```text
커밋 생성
```
