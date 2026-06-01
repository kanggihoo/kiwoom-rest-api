# 02 Ticker State Wiring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** FastAPI lifespan에서 시작하는 Upbit ticker stream의 `on_ticker` callback이 `MarketState`를 업데이트하고 기존 ticker 수신 로그도 유지하게 한다.

**Architecture:** `main.py`에 `handle_ticker(app, ticker)` helper를 두고, lifespan 내부 closure `on_ticker(ticker)`가 app instance를 capture해 helper를 호출한다. 테스트는 실제 Upbit 연결 대신 `run_ticker_stream`과 `log_ticker`를 monkeypatch해 callback 전달, state update, logging 호출만 검증한다.

**Tech Stack:** Python 3.12, FastAPI lifespan, asyncio, pytest, TestClient, RTK.

---

**순서:** 02 / 04
**이전 단계:** [01-snapshot-route.md](./01-snapshot-route.md)
**다음 단계:** [03-market-state-semantics.md](./03-market-state-semantics.md)

### Task 02: Ticker stream을 MarketState와 logging에 연결

**Files:**
- Modify: `apps/backend/tests/test_lifespan.py`
- Modify: `apps/backend/src/upbit_dashboard/main.py`

- [ ] **Step 1: lifespan 테스트에 ticker helper 추가**

`apps/backend/tests/test_lifespan.py` 상단을 다음 import와 helper를 포함하도록 수정한다.

```python
import asyncio

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
```

기존 `test_lifespan_skips_upbit_stream_when_disabled`, `test_lifespan_starts_upbit_stream_by_default`, `test_lifespan_passes_settings_to_upbit_stream`는 helper 아래에 그대로 둔다.

- [ ] **Step 2: 실패하는 runtime wiring 테스트 작성**

`apps/backend/tests/test_lifespan.py`에 다음 테스트를 추가한다.

```python
def test_lifespan_ticker_handler_updates_market_state_and_logs(monkeypatch) -> None:
    captured_kwargs = {}
    logged_markets: list[str] = []

    async def fake_run_ticker_stream(**kwargs) -> None:
        captured_kwargs.update(kwargs)
        await asyncio.Event().wait()

    async def fake_log_ticker(ticker: TickerData) -> None:
        logged_markets.append(ticker.market)

    monkeypatch.setenv("UPBIT_WS_ENABLED", "true")
    monkeypatch.setattr("upbit_dashboard.main.run_ticker_stream", fake_run_ticker_stream)
    monkeypatch.setattr("upbit_dashboard.main.log_ticker", fake_log_ticker)

    with TestClient(create_app()) as client:
        handler = captured_kwargs["on_ticker"]
        asyncio.run(handler(_ticker("KRW-BTC")))

        stored_ticker = client.app.state.market_state.get_ticker("KRW-BTC")
        assert stored_ticker is not None
        assert stored_ticker.trade_price == 1.5
        assert logged_markets == ["KRW-BTC"]
```

- [ ] **Step 3: 테스트 실패 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_lifespan.py::test_lifespan_ticker_handler_updates_market_state_and_logs -q
```

Expected:

```text
AttributeError: module 'upbit_dashboard.main' has no attribute 'log_ticker'
```

- [ ] **Step 4: ticker handler 구현**

`apps/backend/src/upbit_dashboard/main.py` import를 수정한다.

```python
from upbit_dashboard.contracts.quotation import TickerData
from upbit_dashboard.upbit.runner import log_ticker, run_ticker_stream
```

`lifespan()` 위에 helper를 추가한다.

```python
async def handle_ticker(app: FastAPI, ticker: TickerData) -> None:
    app.state.market_state.upsert_ticker(ticker)
    await log_ticker(ticker)
```

`lifespan(app: FastAPI)`의 `if settings.upbit_ws_enabled:` 블록 안에서 `asyncio.create_task(...)` 전에 closure를 추가한다.

```python
        async def on_ticker(ticker: TickerData) -> None:
            await handle_ticker(app, ticker)
```

같은 블록의 `run_ticker_stream(...)` 호출에 `on_ticker=on_ticker`를 추가한다.

```python
        ticker_task = asyncio.create_task(
            run_ticker_stream(
                markets=settings.upbit_ticker_markets,
                endpoint=settings.upbit_ws_endpoint,
                ticket=settings.upbit_ticket,
                on_ticker=on_ticker,
                initial_backoff=settings.initial_backoff_seconds,
                max_backoff=settings.max_backoff_seconds,
            )
        )
```

- [ ] **Step 5: lifespan 테스트 통과 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_lifespan.py -q
```

Expected:

```text
4 passed
```

- [ ] **Step 6: 단계 커밋**

Run:

```bash
rtk proxy git add apps/backend/src/upbit_dashboard/main.py apps/backend/tests/test_lifespan.py
rtk proxy git commit -m "feat: store ticker updates in market state"
```

Expected:

```text
커밋 생성
```
