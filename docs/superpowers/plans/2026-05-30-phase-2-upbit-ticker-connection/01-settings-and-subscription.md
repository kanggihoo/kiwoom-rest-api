# 01 Settings And Subscription Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upbit WebSocket 연결에 필요한 설정과 ticker 구독 메시지 생성을 추가한다.

**Architecture:** `settings.py`는 Phase 2 상수와 `UPBIT_WS_ENABLED` 판별만 책임진다. `client.py`는 이 단계에서 구독 메시지 생성만 제공하고, payload 파싱과 실제 WebSocket 연결은 다음 단계에서 확장한다. `websockets`는 직접 import할 런타임 의존성이므로 backend dependency에 명시한다.

**Tech Stack:** Python 3.12, websockets, pytest, uv, RTK.

---

**순서:** 01 / 06
**이전 단계:** 없음
**다음 단계:** [02-payload-parsing.md](./02-payload-parsing.md)

### Task 01: Upbit 설정과 ticker 구독 메시지 생성

**Files:**
- Modify: `apps/backend/pyproject.toml`
- Modify: `apps/backend/uv.lock`
- Create: `apps/backend/src/upbit_dashboard/upbit/__init__.py`
- Create: `apps/backend/src/upbit_dashboard/upbit/settings.py`
- Create: `apps/backend/src/upbit_dashboard/upbit/client.py`
- Create: `apps/backend/tests/test_upbit_settings.py`

- [ ] **Step 1: 실패하는 설정/구독 메시지 테스트 작성**

`apps/backend/tests/test_upbit_settings.py`를 만든다.

```python
from upbit_dashboard.upbit.client import build_ticker_subscription, normalize_markets
from upbit_dashboard.upbit.settings import (
    DEFAULT_TICKER_MARKETS,
    DEFAULT_TICKET,
    DEFAULT_UPBIT_WS_ENDPOINT,
    is_upbit_ws_enabled,
)


def test_default_upbit_phase2_settings_are_fixed() -> None:
    assert DEFAULT_UPBIT_WS_ENDPOINT == "wss://api.upbit.com/websocket/v1"
    assert DEFAULT_TICKER_MARKETS == ("KRW-BTC", "KRW-ETH")
    assert DEFAULT_TICKET == "upbit-dashboard-phase2"


def test_is_upbit_ws_enabled_defaults_to_true() -> None:
    assert is_upbit_ws_enabled(None) is True
    assert is_upbit_ws_enabled("") is True
    assert is_upbit_ws_enabled("true") is True
    assert is_upbit_ws_enabled("TRUE") is True


def test_is_upbit_ws_enabled_accepts_false_values() -> None:
    assert is_upbit_ws_enabled("false") is False
    assert is_upbit_ws_enabled("0") is False
    assert is_upbit_ws_enabled("off") is False
    assert is_upbit_ws_enabled("no") is False


def test_normalize_markets_trims_and_uppercases_codes() -> None:
    assert normalize_markets([" krw-btc ", "krw-eth"]) == ("KRW-BTC", "KRW-ETH")


def test_build_ticker_subscription_uses_default_format_and_codes() -> None:
    message = build_ticker_subscription([" krw-btc ", "KRW-ETH"])

    assert message == [
        {"ticket": "upbit-dashboard-phase2"},
        {"type": "ticker", "codes": ["KRW-BTC", "KRW-ETH"]},
        {"format": "DEFAULT"},
    ]
```

- [ ] **Step 2: 테스트 실패 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_upbit_settings.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'upbit_dashboard.upbit'
```

- [ ] **Step 3: `websockets` 직접 의존성 추가**

`apps/backend/pyproject.toml`의 dependencies를 다음처럼 수정한다.

```toml
dependencies = [
    "fastapi>=0.136.3",
    "pydantic>=2.13.4",
    "uvicorn[standard]>=0.48.0",
    "websockets>=16.0",
]
```

Lock 파일을 갱신한다.

```bash
rtk proxy uv lock --directory apps/backend
```

Expected:

```text
Resolved ... packages
```

- [ ] **Step 4: Upbit 패키지와 설정 구현**

`apps/backend/src/upbit_dashboard/upbit/__init__.py`를 만든다.

```python
"""Upbit quotation connection helpers."""
```

`apps/backend/src/upbit_dashboard/upbit/settings.py`를 만든다.

```python
import os


DEFAULT_UPBIT_WS_ENDPOINT = "wss://api.upbit.com/websocket/v1"
DEFAULT_UPBIT_REST_MARKETS_URL = "https://api.upbit.com/v1/market/all?is_details=false"
DEFAULT_TICKER_MARKETS = ("KRW-BTC", "KRW-ETH")
DEFAULT_TICKET = "upbit-dashboard-phase2"
DEFAULT_WS_FORMAT = "DEFAULT"
INITIAL_BACKOFF_SECONDS = 1.0
MAX_BACKOFF_SECONDS = 30.0
SMOKE_TIMEOUT_SECONDS = 15.0

_FALSE_VALUES = {"0", "false", "off", "no"}


def is_upbit_ws_enabled(raw_value: str | None = None) -> bool:
    value = os.getenv("UPBIT_WS_ENABLED") if raw_value is None else raw_value
    if value is None or value.strip() == "":
        return True
    return value.strip().lower() not in _FALSE_VALUES
```

- [ ] **Step 5: ticker 구독 메시지 생성 구현**

`apps/backend/src/upbit_dashboard/upbit/client.py`를 만든다.

```python
from collections.abc import Sequence

from upbit_dashboard.upbit.settings import (
    DEFAULT_TICKER_MARKETS,
    DEFAULT_TICKET,
    DEFAULT_WS_FORMAT,
)


def normalize_markets(markets: Sequence[str]) -> tuple[str, ...]:
    normalized = tuple(market.strip().upper() for market in markets if market.strip())
    if not normalized:
        raise ValueError("At least one Upbit Market is required.")
    return normalized


def build_ticker_subscription(
    markets: Sequence[str] = DEFAULT_TICKER_MARKETS,
    ticket: str = DEFAULT_TICKET,
) -> list[dict[str, object]]:
    codes = list(normalize_markets(markets))
    return [
        {"ticket": ticket},
        {"type": "ticker", "codes": codes},
        {"format": DEFAULT_WS_FORMAT},
    ]
```

- [ ] **Step 6: 테스트 통과 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_upbit_settings.py -q
```

Expected:

```text
5 passed
```

- [ ] **Step 7: 단계 커밋**

Run:

```bash
rtk proxy git add apps/backend/pyproject.toml apps/backend/uv.lock apps/backend/src/upbit_dashboard/upbit apps/backend/tests/test_upbit_settings.py
rtk proxy git commit -m "feat: add upbit ticker subscription settings"
```

Expected:

```text
커밋 생성
```
