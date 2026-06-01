# Phase 3 Backend Memory State Implementation Plan Index

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Phase 2에서 수신한 Upbit ticker를 backend process memory의 `MarketState`에 저장하고, `GET /api/snapshot`으로 최신 snapshot을 반환한다.

**Architecture:** FastAPI app은 이미 `app.state.market_state`로 단일 `MarketState` 인스턴스를 가진다. Phase 3는 `run_ticker_stream(..., on_ticker=...)` callback을 `MarketState` 업데이트와 기존 ticker logging을 함께 수행하는 handler에 연결하고, snapshot REST route는 기존 `MarketStateSnapshotResponse` 계약으로 현재 state를 직렬화한다. 자동 테스트는 Upbit 네트워크에 연결하지 않고 route, handler wiring, state semantics만 검증한다.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, pytest, uv, RTK.

---

## 기준 스펙

- [Phase 3 Backend 메모리 상태 저장 설계](../../specs/2026-06-01-phase-3-backend-memory-state-design.md)

## 실행 순서

| 순번 | 문서 | 산출물 | 커밋 메시지 |
| --- | --- | --- | --- |
| 01 | [01-snapshot-route.md](./01-snapshot-route.md) | FastAPI `GET /api/snapshot` route와 route 테스트 | `feat: expose backend market state snapshot` |
| 02 | [02-ticker-state-wiring.md](./02-ticker-state-wiring.md) | Upbit ticker stream `on_ticker` handler가 `MarketState` 업데이트와 logging 수행 | `feat: store ticker updates in market state` |
| 03 | [03-market-state-semantics.md](./03-market-state-semantics.md) | same-Market replacement와 explicit `generated_at` 회귀 테스트 | `test: lock market state snapshot semantics` |
| 04 | [04-verification.md](./04-verification.md) | backend 전체 테스트, route/wiring 확인, 선택 수동 검증 | `feat: add backend market state snapshot` |

## 전체 파일 구조

### Backend source

```text
apps/backend/src/upbit_dashboard/api/router.py
apps/backend/src/upbit_dashboard/api/routes/snapshot.py
apps/backend/src/upbit_dashboard/main.py
```

### Backend tests

```text
apps/backend/tests/test_snapshot.py
apps/backend/tests/test_lifespan.py
apps/backend/tests/test_market_state.py
```

## 전체 검증 명령

모든 단계가 끝나면 repository root에서 다음을 실행한다.

```bash
rtk test uv run --directory apps/backend pytest -q
rtk proxy rg -n "get_snapshot|/api/snapshot|on_ticker|handle_ticker|log_ticker" apps/backend/src/upbit_dashboard apps/backend/tests
rtk git diff --check
```

예상 결과:

```text
backend pytest 통과
snapshot route와 ticker handler wiring 검색 결과 확인
diff whitespace check 통과
```

네트워크를 사용하는 수동 검증은 implementation branch에서 별도로 실행한다.

```bash
make dev-api-no-upbit
curl -s http://localhost:8000/api/snapshot
make dev-api
curl -s http://localhost:8000/api/snapshot
```

## 실행 원칙

- 각 단계는 번호 순서대로 실행한다.
- 각 단계는 테스트를 먼저 작성하고 실패를 확인한다.
- 단계별 커밋을 만든다.
- 자동 테스트는 Upbit 네트워크에 연결하지 않는다.
- `log_ticker()`를 제거하지 않는다.
- `generatedAt`은 snapshot 생성 시각으로 채운다.
- Next.js BFF, frontend WebSocket, 전체 KRW Market 확장은 이 계획에서 구현하지 않는다.

## 계획 자체 검토

- Spec coverage: snapshot route, ticker `MarketState` wiring, logging 유지, empty state 응답, `generatedAt` 정책, network-free verification이 각 단계에 매핑되어 있다.
- Placeholder scan: plan-writing checklist의 placeholder marker 없이 실행 가능한 코드와 명령을 적었다.
- Type consistency: `TickerData`, `MarketStateSnapshotResponse`, `MarketStateSnapshotData.generated_at`, `handle_ticker(app, ticker)`의 이름과 타입은 현재 backend 코드와 일치한다.
