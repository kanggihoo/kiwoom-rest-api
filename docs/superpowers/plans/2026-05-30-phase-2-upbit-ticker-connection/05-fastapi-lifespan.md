# 05 FastAPI Lifespan Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** FastAPI 서버 시작 시 Upbit ticker stream을 기본 자동 시작하고, `UPBIT_WS_ENABLED=false`이면 자동 시작을 생략한다.

**Architecture:** `main.py`를 app factory와 lifespan 구조로 바꾼다. lifespan은 startup에서 background task를 만들고 shutdown에서 cancel/await로 정리한다. 테스트는 `create_app()`을 사용하고, 실제 Upbit 네트워크 대신 `run_ticker_stream`을 monkeypatch한다.

**Tech Stack:** FastAPI, asyncio, pytest, TestClient, RTK.

---

**순서:** 05 / 06
**이전 단계:** [04-smoke-command.md](./04-smoke-command.md)
**다음 단계:** [06-makefile-and-verification.md](./06-makefile-and-verification.md)

### Task 05: FastAPI lifespan 자동 연결 추가

**Files:**
- Modify: `apps/backend/src/upbit_dashboard/main.py`
- Create: `apps/backend/tests/test_lifespan.py`
- Modify: `apps/backend/tests/test_health.py`

- [ ] **Step 1: 실패하는 lifespan 테스트 작성**

`apps/backend/tests/test_lifespan.py`를 만든다.

```python
import asyncio

from fastapi.testclient import TestClient

from upbit_dashboard.main import create_app


def test_lifespan_skips_upbit_stream_when_disabled(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")

    with TestClient(create_app()) as client:
        response = client.get("/health")

        assert response.status_code == 200
        assert client.app.state.upbit_ticker_task is None


def test_lifespan_starts_upbit_stream_by_default(monkeypatch) -> None:
    async def fake_run_ticker_stream() -> None:
        await asyncio.Event().wait()

    monkeypatch.delenv("UPBIT_WS_ENABLED", raising=False)
    monkeypatch.setattr("upbit_dashboard.main.run_ticker_stream", fake_run_ticker_stream)

    with TestClient(create_app()) as client:
        assert client.app.state.upbit_ticker_task is not None
        assert client.app.state.upbit_ticker_task.done() is False
```

`apps/backend/tests/test_health.py`를 다음처럼 수정해 app factory를 사용한다.

```python
from fastapi.testclient import TestClient

from upbit_dashboard.main import create_app


def test_health_returns_ok(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "upbit-dashboard-backend",
    }
```

- [ ] **Step 2: 테스트 실패 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_lifespan.py apps/backend/tests/test_health.py -q
```

Expected:

```text
ImportError: cannot import name 'create_app'
```

- [ ] **Step 3: FastAPI app factory와 lifespan 구현**

`apps/backend/src/upbit_dashboard/main.py`를 다음 내용으로 교체한다.

```python
from contextlib import asynccontextmanager, suppress
import asyncio
import logging
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request

from upbit_dashboard.api.errors import DashboardApiError, make_error_response
from upbit_dashboard.state.market_state import MarketState
from upbit_dashboard.upbit.runner import run_ticker_stream
from upbit_dashboard.upbit.settings import is_upbit_ws_enabled

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    ticker_task: asyncio.Task[None] | None = None

    if is_upbit_ws_enabled():
        ticker_task = asyncio.create_task(run_ticker_stream())
        logger.info("Upbit ticker stream background task created")
    else:
        logger.info("Upbit ticker stream disabled by UPBIT_WS_ENABLED=false")

    app.state.upbit_ticker_task = ticker_task

    try:
        yield
    finally:
        if ticker_task is not None:
            ticker_task.cancel()
            with suppress(asyncio.CancelledError):
                await ticker_task


def create_app() -> FastAPI:
    app = FastAPI(title="Upbit Dashboard API", lifespan=lifespan)
    app.state.market_state = MarketState()
    app.state.upbit_ticker_task = None

    @app.exception_handler(DashboardApiError)
    async def api_error_handler(_: Request, exc: DashboardApiError):
        return make_error_response(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            status_code=exc.status_code,
        )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "upbit-dashboard-backend"}

    return app


app = create_app()
```

- [ ] **Step 4: lifespan 테스트 통과 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_lifespan.py apps/backend/tests/test_health.py -q
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
rtk proxy git add apps/backend/src/upbit_dashboard/main.py apps/backend/tests/test_lifespan.py apps/backend/tests/test_health.py
rtk proxy git commit -m "feat: start upbit ticker stream with backend"
```

Expected:

```text
커밋 생성
```
