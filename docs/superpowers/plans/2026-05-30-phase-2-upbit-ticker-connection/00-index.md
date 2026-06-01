# Phase 2 Upbit Ticker Connection Implementation Plan Index

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** FastAPI 백엔드가 Upbit 공개 REST/WebSocket endpoint와 실제 통신하고, `KRW-BTC`, `KRW-ETH` ticker를 Phase 1 계약으로 변환해 로그로 확인한다.

**Architecture:** Upbit 연결은 `upbit_dashboard.upbit` 패키지로 분리하고, 구독 메시지 생성/파싱/client/runner를 책임별로 나눈다. smoke command와 FastAPI lifespan은 같은 client/runner 흐름을 사용하며, root `Makefile`은 사람이 실행하는 짧은 명령만 제공한다. 네트워크 테스트는 수동 smoke로 분리하고, 자동 테스트는 payload/설정/backoff/lifespan 제어만 검증한다.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, websockets, httpx, pytest, uv, Makefile, RTK.

---

## 기준 스펙

- [Phase 2 Upbit ticker 최소 연결 설계](../../specs/2026-05-30-phase-2-upbit-ticker-connection-design.md)

## 실행 순서

| 순번 | 문서 | 산출물 | 커밋 메시지 |
| --- | --- | --- | --- |
| 01 | [01-settings-and-subscription.md](./01-settings-and-subscription.md) | WebSocket 직접 의존성, Upbit 설정, ticker 구독 메시지 생성 | `feat: add upbit ticker subscription settings` |
| 02 | [02-payload-parsing.md](./02-payload-parsing.md) | Upbit WebSocket payload 파싱, error payload 분리, `TickerData` 변환 | `feat: parse upbit ticker websocket payloads` |
| 03 | [03-stream-runner.md](./03-stream-runner.md) | 단일 WebSocket stream client, reconnect/backoff runner | `feat: add upbit ticker stream runner` |
| 04 | [04-smoke-command.md](./04-smoke-command.md) | FastAPI 없이 실행 가능한 Upbit REST/WS smoke command | `feat: add upbit connection smoke command` |
| 05 | [05-fastapi-lifespan.md](./05-fastapi-lifespan.md) | FastAPI startup 자동 연결, `UPBIT_WS_ENABLED=false` kill switch, shutdown 정리 | `feat: start upbit ticker stream with backend` |
| 06 | [06-makefile-and-verification.md](./06-makefile-and-verification.md) | root `Makefile` 타겟과 전체 검증 | `chore: add phase 2 local make targets` |

## 전체 파일 구조

### Backend source

```text
apps/backend/pyproject.toml
apps/backend/uv.lock
apps/backend/src/upbit_dashboard/main.py
apps/backend/src/upbit_dashboard/upbit/__init__.py
apps/backend/src/upbit_dashboard/upbit/settings.py
apps/backend/src/upbit_dashboard/upbit/client.py
apps/backend/src/upbit_dashboard/upbit/runner.py
apps/backend/src/upbit_dashboard/tools/__init__.py
apps/backend/src/upbit_dashboard/tools/smoke_upbit_connection.py
```

### Backend tests

```text
apps/backend/tests/test_upbit_settings.py
apps/backend/tests/test_upbit_client.py
apps/backend/tests/test_upbit_runner.py
apps/backend/tests/test_upbit_smoke.py
apps/backend/tests/test_lifespan.py
```

### Root command entrypoint

```text
Makefile
```

## 전체 검증 명령

모든 단계가 끝나면 repository root에서 다음을 실행한다.

```bash
rtk test make test-api
rtk proxy make -n upbit-smoke
rtk proxy make -n dev-api
rtk proxy make -n dev-api-no-upbit
rtk git diff --check
```

예상 결과:

```text
backend pytest 통과
make dry-run 명령 출력
diff whitespace check 통과
```

네트워크를 사용하는 수동 검증은 implementation branch에서 별도로 실행한다.

```bash
make upbit-smoke
make dev-api
make dev-api-no-upbit
```

## 실행 원칙

- 각 단계는 번호 순서대로 실행한다.
- 각 단계는 테스트를 먼저 작성하고 실패를 확인한다.
- 단계별 커밋을 만든다.
- 자동 테스트는 Upbit 네트워크에 연결하지 않는다.
- 수신 ticker를 `MarketState`에 저장하지 않는다.
- `GET /api/snapshot`, 프론트 WebSocket, 전체 KRW Market 확장은 이 계획에서 구현하지 않는다.
