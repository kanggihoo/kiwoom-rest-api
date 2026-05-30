# Phase 1 API Contracts Implementation Plan Index

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Phase 1 API 이벤트 계약 스펙을 백엔드 Pydantic 모델, 프론트 TypeScript 타입, 테스트, 문서 갱신으로 구현한다.

**Architecture:** 백엔드 계약은 `apps/backend/src/upbit_dashboard/contracts/` 아래에 책임별 파일로 둔다. 프론트 계약은 `apps/web/src/lib/contracts/` 아래에 백엔드 JSON 출력 구조와 같은 camelCase 타입으로 둔다. 각 단계는 테스트를 먼저 작성하고, 최소 구현 후 검증하고, 단계별 커밋으로 마무리한다.

**Tech Stack:** FastAPI, Pydantic v2, pytest, Next.js, TypeScript, pnpm, uv, RTK.

---

## 기준 스펙

- [Phase 1 API 이벤트 계약 설계](../../specs/2026-05-30-phase-1-api-contracts-design.md)

## 실행 순서

| 순번 | 문서 | 산출물 | 커밋 메시지 |
| --- | --- | --- | --- |
| 01 | [01-backend-errors-and-enums.md](./01-backend-errors-and-enums.md) | 백엔드 error 계약, error code, 공통 enum 시작점 | `feat: add backend error contract models` |
| 02 | [02-backend-websocket-event-contracts.md](./02-backend-websocket-event-contracts.md) | WebSocket event Pydantic 모델 | `feat: add websocket event contract models` |
| 03 | [03-backend-rest-contracts.md](./03-backend-rest-contracts.md) | REST response Pydantic 모델 | `feat: add rest response contract models` |
| 04 | [04-upbit-ticker-raw-and-mapper.md](./04-upbit-ticker-raw-and-mapper.md) | Upbit ticker raw 모델과 mapper | `feat: add upbit ticker contract mapper` |
| 05 | [05-frontend-contract-types.md](./05-frontend-contract-types.md) | 프론트 TypeScript 계약 타입 | `feat: add frontend api contract types` |
| 06 | [06-docs-and-verification.md](./06-docs-and-verification.md) | 개발 순서 문서 갱신, 전체 검증 | `docs: update phase 1 development sequence` |

## 전체 파일 구조

### Backend

```text
apps/backend/src/upbit_dashboard/contracts/__init__.py
apps/backend/src/upbit_dashboard/contracts/errors.py
apps/backend/src/upbit_dashboard/contracts/events.py
apps/backend/src/upbit_dashboard/contracts/rest.py
apps/backend/src/upbit_dashboard/contracts/upbit.py
apps/backend/src/upbit_dashboard/contracts/mappers.py
apps/backend/tests/test_error_contracts.py
apps/backend/tests/test_contract_serialization.py
apps/backend/tests/test_upbit_ticker_mapper.py
```

### Frontend

```text
apps/web/src/lib/contracts/events.ts
apps/web/src/lib/contracts/rest.ts
apps/web/src/lib/contracts/errors.ts
```

### Docs

```text
docs/development-sequence.md
```

## 전체 검증 명령

모든 단계가 끝나면 root에서 다음을 실행한다.

```bash
rtk test make test-api
rtk test make lint-web
rtk test make build-web
rtk git diff --check
```

예상 결과:

```text
backend pytest 통과
web lint 통과
web build 통과
diff whitespace check 통과
```

## 실행 원칙

- 기존 변경사항인 `apps/web/src/app/api/health/route.ts`는 Phase 1 계약 구현과 무관하면 건드리지 않는다.
- 각 단계는 문서 순서대로 실행한다.
- 각 단계의 테스트는 실패 확인 후 구현한다.
- 단계별 커밋을 만든다.
- Upbit 실제 연결, BFF route 구현, UI 구현은 이 계획에서 하지 않는다.
