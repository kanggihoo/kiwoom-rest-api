# 01 Backend Errors And Enums Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Phase 1 REST/WebSocket 에러 envelope와 error code 매핑을 백엔드 Pydantic 모델로 구현한다.

**Architecture:** `errors.py`는 error envelope, REST/WebSocket error code enum, REST status 매핑만 책임진다. WebSocket event enum은 다음 단계에서 `events.py`에 둔다. 이 단계는 error 계약의 400/422, 418/429 분리를 테스트로 고정한다.

**Tech Stack:** Python 3.12, Pydantic v2, pytest, RTK.

---

**순서:** 01 / 06
**이전 단계:** 없음
**다음 단계:** [02-backend-websocket-event-contracts.md](./02-backend-websocket-event-contracts.md)

### Task 01: 백엔드 에러 계약 모델 추가

**Files:**
- Create: `apps/backend/src/upbit_dashboard/contracts/__init__.py`
- Create: `apps/backend/src/upbit_dashboard/contracts/errors.py`
- Create: `apps/backend/tests/test_error_contracts.py`

- [ ] **Step 1: 실패하는 에러 계약 테스트 작성**

`apps/backend/tests/test_error_contracts.py`를 만든다.

```python
from datetime import datetime, timezone

from upbit_dashboard.contracts.errors import (
    ErrorData,
    ErrorEnvelope,
    RestErrorCode,
    WebSocketErrorCode,
    rest_status_for_error,
)


def test_error_envelope_serializes_code_as_string() -> None:
    envelope = ErrorEnvelope(
        timestamp=datetime(2026, 5, 30, 3, 0, tzinfo=timezone.utc),
        data=ErrorData(
            code=RestErrorCode.RATE_LIMITED,
            message="Upbit request rate limit exceeded.",
            details={
                "upbitStatus": 429,
                "rateLimitGroup": "candle",
                "remainingSec": 0,
            },
        ),
    )

    assert envelope.model_dump(mode="json") == {
        "type": "error",
        "timestamp": "2026-05-30T03:00:00Z",
        "data": {
            "code": "RATE_LIMITED",
            "message": "Upbit request rate limit exceeded.",
            "details": {
                "upbitStatus": 429,
                "rateLimitGroup": "candle",
                "remainingSec": 0,
            },
        },
    }


def test_rest_error_status_mapping_separates_bad_request_and_validation() -> None:
    assert rest_status_for_error(RestErrorCode.BAD_REQUEST) == 400
    assert rest_status_for_error(RestErrorCode.VALIDATION_ERROR) == 422


def test_rest_error_status_mapping_separates_rate_limit_and_block() -> None:
    assert rest_status_for_error(RestErrorCode.TEMPORARILY_BLOCKED) == 418
    assert rest_status_for_error(RestErrorCode.RATE_LIMITED) == 429


def test_websocket_error_codes_include_upbit_error_cases() -> None:
    assert WebSocketErrorCode.UPBIT_WS_ERROR.value == "UPBIT_WS_ERROR"
    assert WebSocketErrorCode.RATE_LIMITED.value == "RATE_LIMITED"
    assert WebSocketErrorCode.TEMPORARILY_BLOCKED.value == "TEMPORARILY_BLOCKED"
```

- [ ] **Step 2: 테스트 실패 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_error_contracts.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'upbit_dashboard.contracts'
```

- [ ] **Step 3: contracts 패키지와 error 모델 구현**

`apps/backend/src/upbit_dashboard/contracts/__init__.py`를 만든다.

```python
"""API contract models for the Upbit dashboard."""
```

`apps/backend/src/upbit_dashboard/contracts/errors.py`를 만든다.

```python
from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


class RestErrorCode(StrEnum):
    BAD_REQUEST = "BAD_REQUEST"
    NOT_FOUND = "NOT_FOUND"
    TEMPORARILY_BLOCKED = "TEMPORARILY_BLOCKED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    UPBIT_BAD_REQUEST = "UPBIT_BAD_REQUEST"
    UPBIT_ERROR = "UPBIT_ERROR"
    UPBIT_TIMEOUT = "UPBIT_TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class WebSocketErrorCode(StrEnum):
    INVALID_MESSAGE = "INVALID_MESSAGE"
    UNSUPPORTED_MESSAGE_TYPE = "UNSUPPORTED_MESSAGE_TYPE"
    INVALID_MARKET = "INVALID_MARKET"
    BAD_REQUEST = "BAD_REQUEST"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    TEMPORARILY_BLOCKED = "TEMPORARILY_BLOCKED"
    UPBIT_WS_ERROR = "UPBIT_WS_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


REST_ERROR_STATUS: dict[RestErrorCode, int] = {
    RestErrorCode.BAD_REQUEST: 400,
    RestErrorCode.NOT_FOUND: 404,
    RestErrorCode.TEMPORARILY_BLOCKED: 418,
    RestErrorCode.VALIDATION_ERROR: 422,
    RestErrorCode.RATE_LIMITED: 429,
    RestErrorCode.UPBIT_BAD_REQUEST: 502,
    RestErrorCode.UPBIT_ERROR: 502,
    RestErrorCode.UPBIT_TIMEOUT: 504,
    RestErrorCode.INTERNAL_ERROR: 500,
}


class ErrorData(BaseModel):
    code: RestErrorCode | WebSocketErrorCode = Field(
        description="앱 내부 에러 코드. HTTP status와 별도로 프론트 분기에 사용한다.",
    )
    message: str = Field(description="사람이 읽을 수 있는 짧은 에러 설명.")
    details: dict[str, Any] | None = Field(
        default=None,
        description="Upbit 원본 status/error.name/Remaining-Req 등 추가 맥락.",
    )


class ErrorEnvelope(BaseModel):
    type: Literal["error"] = Field(
        default="error",
        description="에러 envelope type.",
    )
    timestamp: datetime = Field(
        description="우리 서버가 에러 응답 또는 이벤트를 만든 시각.",
    )
    data: ErrorData = Field(description="에러 상세 payload.")


def rest_status_for_error(code: RestErrorCode) -> int:
    return REST_ERROR_STATUS[code]
```

- [ ] **Step 4: 테스트 통과 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_error_contracts.py -q
```

Expected:

```text
4 passed
```

- [ ] **Step 5: 단계 커밋**

Run:

```bash
rtk git add apps/backend/src/upbit_dashboard/contracts/__init__.py apps/backend/src/upbit_dashboard/contracts/errors.py apps/backend/tests/test_error_contracts.py
rtk git commit -m "feat: add backend error contract models"
```

Expected:

```text
커밋 생성
```
