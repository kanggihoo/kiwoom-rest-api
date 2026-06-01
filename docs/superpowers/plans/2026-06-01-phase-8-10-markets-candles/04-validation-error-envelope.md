# 04 Validation Error Envelope Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** FastAPI request validation 실패도 기존 REST error envelope로 반환하게 만들어 `/api/candles`와 이후 browser-facing REST route의 오류 형태를 통일한다.

**Architecture:** 기존 `DashboardApiError` handler는 유지하고, `RequestValidationError` handler를 추가한다. Handler는 FastAPI validation error를 `VALIDATION_ERROR` envelope와 HTTP 422로 변환한다.

**Tech Stack:** Python 3.12, FastAPI exception handlers, pytest, TestClient, RTK.

---

**순서:** 04 / 07  
**이전 단계:** [03-candles-route.md](./03-candles-route.md)  
**다음 단계:** [05-all-krw-ticker-wiring.md](./05-all-krw-ticker-wiring.md)

### Task 01: validation error envelope 테스트 작성

**Files:**
- Modify: `apps/backend/tests/test_exception_handlers.py`
- Modify: `apps/backend/src/upbit_dashboard/api/exception_handlers.py`

- [ ] **Step 1: 실패하는 테스트 추가**

`apps/backend/tests/test_exception_handlers.py`에 다음 테스트를 추가한다.

```python
from fastapi import Query


def test_register_exception_handlers_maps_request_validation_error() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/requires-count")
    def requires_count(count: int = Query(le=200)) -> dict[str, int]:
        return {"count": count}

    response = TestClient(app).get("/requires-count?count=201")

    assert response.status_code == 422
    body = response.json()
    assert body["type"] == "error"
    assert body["data"]["code"] == "VALIDATION_ERROR"
    assert body["data"]["message"] == "Request validation failed."
    assert body["data"]["details"]["errors"][0]["loc"] == ["query", "count"]
```

- [ ] **Step 2: 테스트 실패 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_exception_handlers.py -q
```

Expected:

```text
기본 FastAPI validation response가 반환되어 assertion 실패
```

### Task 02: RequestValidationError handler 구현

**Files:**
- Modify: `apps/backend/src/upbit_dashboard/api/exception_handlers.py`

- [ ] **Step 1: handler 추가**

`apps/backend/src/upbit_dashboard/api/exception_handlers.py`를 다음 형태로 수정한다.

```python
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from upbit_dashboard.api.errors import DashboardApiError, make_error_response
from upbit_dashboard.contracts.errors import RestErrorCode


async def dashboard_api_error_handler(_: Request, exc: DashboardApiError):
    return make_error_response(
        code=exc.code,
        message=exc.message,
        details=exc.details,
        status_code=exc.status_code,
    )


async def request_validation_error_handler(_: Request, exc: RequestValidationError):
    return make_error_response(
        code=RestErrorCode.VALIDATION_ERROR,
        message="Request validation failed.",
        details={"errors": exc.errors()},
        status_code=422,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DashboardApiError, dashboard_api_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
```

- [ ] **Step 2: exception handler 테스트 통과 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_exception_handlers.py -q
```

Expected:

```text
passed
```

- [ ] **Step 3: candles validation 회귀 테스트 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_candles_route.py::test_candles_route_rejects_count_above_200 -q
```

Expected:

```text
1 passed
```

- [ ] **Step 4: 단계 커밋**

Run:

```bash
rtk proxy git add apps/backend/src/upbit_dashboard/api/exception_handlers.py apps/backend/tests/test_exception_handlers.py
rtk proxy git commit -m "feat: normalize backend rest validation errors"
```

Expected:

```text
커밋 생성
```
