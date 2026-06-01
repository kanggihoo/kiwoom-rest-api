# Python Rich Logging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** FastAPI 백엔드의 Python 표준 로깅, uvicorn 로깅, Rich 컬러 로그 설정을 하나의 설정 파일에서 관리한다.

**Architecture:** `upbit_dashboard.logging_config`가 환경변수를 읽어 `logging.config.dictConfig(...)` 설정 딕셔너리를 만들고 적용한다. FastAPI 앱 진입점과 smoke tool은 같은 `configure_logging()`을 호출해 `upbit_dashboard`, `uvicorn`, `uvicorn.error`, `uvicorn.access`, root logger를 동일한 정책으로 출력한다.

**Tech Stack:** Python 3.12, FastAPI, uvicorn, standard library `logging`, `logging.config.dictConfig`, Rich, pytest, uv

---

## 범위 확인

이 계획은 Python 백엔드 로깅 설정만 다룬다.

Next.js BFF 로깅, 운영 JSON 로그, 파일 로그, 로그 로테이션, 외부 수집기 연동은 포함하지 않는다.

## 파일 구조

- Create: `apps/backend/src/upbit_dashboard/logging_config.py`
- Modify: `apps/backend/src/upbit_dashboard/main.py`
- Modify: `apps/backend/src/upbit_dashboard/tools/smoke_upbit_connection.py`
- Modify: `apps/backend/pyproject.toml`
- Create: `apps/backend/tests/test_logging_config.py`

`logging_config.py`는 로깅 설정의 단일 책임 파일이다. 환경변수 파싱, plain/rich dictConfig 생성, 실제 적용 함수만 가진다.

`main.py`는 FastAPI 앱 import 시점에 공통 로깅을 적용한다. 기존 lifespan과 앱 생성 책임은 유지한다.

`smoke_upbit_connection.py`는 자체 `basicConfig`를 제거하고 공통 로깅 설정을 사용한다.

`pyproject.toml`은 Rich 런타임 의존성을 추가한다.

`test_logging_config.py`는 환경변수 파싱과 dictConfig 구조를 검증한다. 실제 터미널 색상 출력은 단위 테스트 대상이 아니다.

---

### Task 1: Rich 의존성 추가

**Files:**
- Modify: `apps/backend/pyproject.toml`

- [ ] **Step 1: `rich` 런타임 의존성 추가**

`apps/backend/pyproject.toml`의 `[project].dependencies`에 `rich`를 추가한다.

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
    "pydantic>=2.13.4",
    "rich>=14.0.0",
    "uvicorn[standard]>=0.48.0",
    "websockets>=16.0",
]
```

- [ ] **Step 2: 의존성 lock 갱신**

Run:

```bash
uv lock --directory apps/backend
```

Expected: `apps/backend/uv.lock`가 생성되어 있거나 갱신된다.

- [ ] **Step 3: 커밋**

```bash
git add apps/backend/pyproject.toml apps/backend/uv.lock
git commit -m "chore: add rich logging dependency"
```

---

### Task 2: 로깅 설정 단위 테스트 작성

**Files:**
- Create: `apps/backend/tests/test_logging_config.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`apps/backend/tests/test_logging_config.py`를 생성한다.

```python
import logging

import pytest

from upbit_dashboard.logging_config import (
    DEFAULT_LOG_FORMAT,
    DEFAULT_LOG_LEVEL,
    build_logging_config,
    get_log_format,
    get_log_level,
)


def test_default_log_format_is_plain(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LOG_FORMAT", raising=False)

    assert get_log_format() == DEFAULT_LOG_FORMAT
    assert get_log_format() == "plain"


def test_unknown_log_format_falls_back_to_plain(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_FORMAT", "unknown")

    assert get_log_format() == "plain"


def test_rich_log_format_is_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_FORMAT", "rich")

    assert get_log_format() == "rich"


def test_log_format_is_case_insensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_FORMAT", "RICH")

    assert get_log_format() == "rich"


def test_default_log_level_is_info(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    assert get_log_level() == DEFAULT_LOG_LEVEL
    assert get_log_level() == "INFO"


def test_debug_log_level_is_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "debug")

    assert get_log_level() == "DEBUG"


def test_unknown_log_level_falls_back_to_info(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "verbose")

    assert get_log_level() == "INFO"


def test_plain_logging_config_contains_expected_loggers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_FORMAT", "plain")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    config = build_logging_config()

    assert config["version"] == 1
    assert config["disable_existing_loggers"] is False
    assert config["root"] == {"handlers": ["console"], "level": "DEBUG"}
    assert config["handlers"]["console"]["class"] == "logging.StreamHandler"
    assert config["handlers"]["console"]["formatter"] == "plain"
    assert config["formatters"]["plain"]["format"] == "%(asctime)s %(levelname)-8s [%(name)s] %(message)s"
    assert config["formatters"]["plain"]["datefmt"] == "%Y-%m-%d %H:%M:%S"

    for logger_name in ("upbit_dashboard", "uvicorn", "uvicorn.error", "uvicorn.access"):
        assert config["loggers"][logger_name] == {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        }


def test_rich_logging_config_uses_rich_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_FORMAT", "rich")
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    config = build_logging_config()

    assert config["handlers"]["console"]["class"] == "rich.logging.RichHandler"
    assert config["handlers"]["console"]["level"] == "INFO"
    assert config["handlers"]["console"]["rich_tracebacks"] is True
    assert config["handlers"]["console"]["show_time"] is True
    assert config["handlers"]["console"]["show_level"] is True
    assert config["handlers"]["console"]["show_path"] is True
    assert config["handlers"]["console"]["enable_link_path"] is True
    assert config["handlers"]["console"]["markup"] is False
    assert config["handlers"]["console"]["formatter"] == "rich"
    assert config["formatters"]["rich"]["format"] == "%(message)s"


def test_known_logging_level_names_are_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    for level_name in logging.getLevelNamesMapping():
        if isinstance(logging.getLevelName(level_name), int):
            monkeypatch.setenv("LOG_LEVEL", level_name.lower())
            assert get_log_level() == level_name
```

- [ ] **Step 2: 테스트 실패 확인**

Run:

```bash
uv run --directory apps/backend pytest tests/test_logging_config.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'upbit_dashboard.logging_config'`.

- [ ] **Step 3: 커밋하지 않음**

테스트는 아직 실패 상태이므로 커밋하지 않는다.

---

### Task 3: `logging_config.py` 구현

**Files:**
- Create: `apps/backend/src/upbit_dashboard/logging_config.py`
- Test: `apps/backend/tests/test_logging_config.py`

- [ ] **Step 1: 최소 구현 작성**

`apps/backend/src/upbit_dashboard/logging_config.py`를 생성한다.

```python
from __future__ import annotations

import logging
import logging.config
import os
from typing import Any

DEFAULT_LOG_FORMAT = "plain"
DEFAULT_LOG_LEVEL = "INFO"
SUPPORTED_LOG_FORMATS = {"plain", "rich"}

APP_LOGGERS = (
    "upbit_dashboard",
    "uvicorn",
    "uvicorn.error",
    "uvicorn.access",
)

PLAIN_LOG_FORMAT = "%(asctime)s %(levelname)-8s [%(name)s] %(filename)s:%(lineno)d %(message)s"
PLAIN_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
RICH_LOG_FORMAT = "%(message)s"


def get_log_format(raw_value: str | None = None) -> str:
    value = os.getenv("LOG_FORMAT") if raw_value is None else raw_value
    if value is None or value.strip() == "":
        return DEFAULT_LOG_FORMAT

    normalized = value.strip().lower()
    if normalized not in SUPPORTED_LOG_FORMATS:
        return DEFAULT_LOG_FORMAT
    return normalized


def get_log_level(raw_value: str | None = None) -> str:
    value = os.getenv("LOG_LEVEL") if raw_value is None else raw_value
    if value is None or value.strip() == "":
        return DEFAULT_LOG_LEVEL

    normalized = value.strip().upper()
    level_value = logging.getLevelNamesMapping().get(normalized)
    if not isinstance(level_value, int):
        return DEFAULT_LOG_LEVEL
    return normalized


def build_logging_config() -> dict[str, Any]:
    log_format = get_log_format()
    log_level = get_log_level()

    if log_format == "rich":
        return _build_rich_config(log_level)
    return _build_plain_config(log_level)


def configure_logging() -> None:
    logging.config.dictConfig(build_logging_config())


def _build_plain_config(log_level: str) -> dict[str, Any]:
    return _base_config(
        log_level=log_level,
        formatter_name="plain",
        formatters={
            "plain": {
                "format": PLAIN_LOG_FORMAT,
                "datefmt": PLAIN_DATE_FORMAT,
            }
        },
        handler={
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "plain",
            "stream": "ext://sys.stderr",
        },
    )


def _build_rich_config(log_level: str) -> dict[str, Any]:
    return _base_config(
        log_level=log_level,
        formatter_name="rich",
        formatters={
            "rich": {
                "format": RICH_LOG_FORMAT,
            }
        },
        handler={
            "class": "rich.logging.RichHandler",
            "level": log_level,
            "formatter": "rich",
            "rich_tracebacks": True,
            "show_time": True,
            "show_level": True,
            "show_path": True,
            "enable_link_path": True,
            "markup": False,
        },
    )


def _base_config(
    *,
    log_level: str,
    formatter_name: str,
    formatters: dict[str, dict[str, Any]],
    handler: dict[str, Any],
) -> dict[str, Any]:
    loggers = {
        logger_name: {
            "handlers": ["console"],
            "level": log_level,
            "propagate": False,
        }
        for logger_name in APP_LOGGERS
    }

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "handlers": {
            "console": handler,
        },
        "root": {
            "handlers": ["console"],
            "level": log_level,
        },
        "loggers": loggers,
    }
```

- [ ] **Step 2: 테스트 통과 확인**

Run:

```bash
uv run --directory apps/backend pytest tests/test_logging_config.py -v
```

Expected: PASS.

- [ ] **Step 3: 커밋**

```bash
git add apps/backend/src/upbit_dashboard/logging_config.py apps/backend/tests/test_logging_config.py
git commit -m "feat: add backend logging configuration"
```

---

### Task 4: FastAPI 앱 진입점에 공통 로깅 적용

**Files:**
- Modify: `apps/backend/src/upbit_dashboard/main.py`
- Test: `apps/backend/tests/test_health.py`

- [ ] **Step 1: `main.py` 수정**

`apps/backend/src/upbit_dashboard/main.py` 상단 import 영역에 `configure_logging`을 추가하고, `logger` 생성 전에 호출한다.

```python
from contextlib import asynccontextmanager, suppress
import asyncio
import logging
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request

from upbit_dashboard.api.errors import DashboardApiError, make_error_response
from upbit_dashboard.logging_config import configure_logging
from upbit_dashboard.state.market_state import MarketState
from upbit_dashboard.upbit.runner import run_ticker_stream
from upbit_dashboard.upbit.settings import is_upbit_ws_enabled

configure_logging()

logger = logging.getLogger(__name__)
```

파일의 나머지 FastAPI lifespan, `create_app()`, `app = create_app()` 구조는 유지한다.

- [ ] **Step 2: 앱 import 관련 기존 테스트 실행**

Run:

```bash
uv run --directory apps/backend pytest tests/test_health.py tests/test_lifespan.py -v
```

Expected: PASS.

- [ ] **Step 3: 커밋**

```bash
git add apps/backend/src/upbit_dashboard/main.py
git commit -m "feat: configure logging for fastapi app"
```

---

### Task 5: smoke tool에 공통 로깅 적용

**Files:**
- Modify: `apps/backend/src/upbit_dashboard/tools/smoke_upbit_connection.py`
- Test: `apps/backend/tests/test_upbit_smoke.py`

- [ ] **Step 1: smoke tool import 추가**

`apps/backend/src/upbit_dashboard/tools/smoke_upbit_connection.py`에 `configure_logging` import를 추가한다.

```python
from upbit_dashboard.logging_config import configure_logging
```

- [ ] **Step 2: `basicConfig` 제거 후 공통 설정 호출**

`main()`을 아래 형태로 바꾼다.

```python
def main() -> None:
    configure_logging()
    try:
        asyncio.run(main_async())
    except Exception:
        logger.exception("smoke failed")
        raise SystemExit(1)
```

기존 아래 라인은 제거한다.

```python
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
```

상단의 `import logging`과 `logger = logging.getLogger(__name__)`는 유지한다.

- [ ] **Step 3: smoke 관련 테스트 실행**

Run:

```bash
uv run --directory apps/backend pytest tests/test_upbit_smoke.py -v
```

Expected: PASS.

- [ ] **Step 4: 커밋**

```bash
git add apps/backend/src/upbit_dashboard/tools/smoke_upbit_connection.py
git commit -m "feat: reuse logging config in upbit smoke tool"
```

---

### Task 6: 통합 테스트와 로컬 실행 확인

**Files:**
- No file changes expected

- [ ] **Step 1: 백엔드 테스트 전체 실행**

Run:

```bash
uv run --directory apps/backend pytest -v
```

Expected: PASS.

- [ ] **Step 2: 기본 plain 로그 실행 확인**

Run:

```bash
UPBIT_WS_ENABLED=false make dev-api
```

Expected: 일반 텍스트 로그가 출력된다. 예시는 다음과 같다.

```text
2026-06-01 12:34:56 INFO     [uvicorn.error] server.py:84 Started server process
2026-06-01 12:34:56 INFO     [upbit_dashboard.main] main.py:24 Upbit ticker stream disabled by UPBIT_WS_ENABLED=false
```

확인 후 서버 프로세스를 중지한다.

- [ ] **Step 3: Rich 로그 실행 확인**

Run:

```bash
LOG_FORMAT=rich LOG_LEVEL=DEBUG UPBIT_WS_ENABLED=false make dev-api
```

Expected: RichHandler 기반 컬러 로그가 출력된다. 출력에는 로그 레벨, 메시지, 로그 호출 파일과 라인 번호가 보여야 한다.

확인 후 서버 프로세스를 중지한다.

- [ ] **Step 4: smoke tool Rich 로그 실행 확인**

Run:

```bash
LOG_FORMAT=rich LOG_LEVEL=DEBUG make upbit-smoke
```

Expected: smoke tool 로그도 RichHandler 형식으로 출력된다. 네트워크 상태에 따라 Upbit 연결 자체가 실패할 수 있지만, 실패 로그는 Rich traceback 형식으로 출력되어야 한다.

- [ ] **Step 5: 최종 커밋**

통합 확인 중 추가 수정이 있었다면 커밋한다.

```bash
git status --short
git add apps/backend/pyproject.toml apps/backend/uv.lock apps/backend/src/upbit_dashboard/logging_config.py apps/backend/src/upbit_dashboard/main.py apps/backend/src/upbit_dashboard/tools/smoke_upbit_connection.py apps/backend/tests/test_logging_config.py
git commit -m "feat: unify backend logging configuration"
```

추가 수정이 없고 이전 task 커밋들이 이미 완료되어 있다면 이 단계의 커밋은 생략한다.

---

## 완료 기준

- `apps/backend/src/upbit_dashboard/logging_config.py`가 로깅 설정의 단일 관리 파일이다.
- `LOG_FORMAT` 기본값은 `plain`이다.
- `LOG_FORMAT=rich`에서 RichHandler가 사용된다.
- `LOG_LEVEL` 기본값은 `INFO`이다.
- 알 수 없는 `LOG_FORMAT`은 `plain`으로 fallback한다.
- 알 수 없는 `LOG_LEVEL`은 `INFO`로 fallback한다.
- plain 로그에는 `filename:lineno`가 포함된다.
- Rich 로그에는 `show_path=True`와 `enable_link_path=True`로 로그 호출 파일과 라인 번호가 표시된다.
- `upbit_dashboard`, `uvicorn`, `uvicorn.error`, `uvicorn.access`, root logger가 같은 콘솔 핸들러 정책을 사용한다.
- uvicorn reload 중에도 로그 핸들러가 중복 누적되지 않는다.
- smoke tool이 `logging.basicConfig(...)`를 직접 호출하지 않는다.
- 백엔드 테스트가 통과한다.

## 자체 검토 결과

- Spec coverage: 설계 문서의 환경변수, dictConfig, Rich 의존성, uvicorn 통합, FastAPI 적용, smoke tool 적용, fallback, 테스트 범위를 모두 task에 배치했다.
- Placeholder scan: `TBD`, `TODO`, `나중에`, `적절한 처리` 같은 미완성 지시어는 사용하지 않았다.
- Type consistency: `configure_logging()`, `build_logging_config()`, `get_log_format()`, `get_log_level()` 이름을 테스트와 구현 단계에서 동일하게 사용했다.
