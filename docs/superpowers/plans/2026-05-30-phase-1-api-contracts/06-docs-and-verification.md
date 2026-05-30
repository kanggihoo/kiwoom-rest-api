# 06 Docs And Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `docs/development-sequence.md`의 Phase 1 설명을 실제 구현 계획과 맞추고, 전체 Phase 1 계약 구현을 검증한다.

**Architecture:** 세부 계약 원문은 `docs/superpowers/specs/2026-05-30-phase-1-api-contracts-design.md`에 둔다. `docs/development-sequence.md`에는 개발 순서 문서답게 Phase 1의 작업 단위와 완료 기준만 요약한다.

**Tech Stack:** Markdown, RTK, pytest, pnpm, Makefile.

---

**순서:** 06 / 06
**이전 단계:** [05-frontend-contract-types.md](./05-frontend-contract-types.md)
**다음 단계:** 없음

### Task 06: 개발 순서 문서 갱신과 전체 검증

**Files:**
- Modify: `docs/development-sequence.md`

- [ ] **Step 1: Phase 1 섹션을 구체화**

`docs/development-sequence.md`의 `## Phase 1. API 이벤트 계약 정의` 섹션을 아래 내용으로 교체한다.

```markdown
## Phase 1. API 이벤트 계약 정의

목표: 실제 Upbit 연결 전에 프론트와 백엔드가 주고받을 REST/WebSocket 메시지 형태를 Pydantic 모델, TypeScript 타입, 테스트로 고정한다.

근거 문서:

- `docs/superpowers/specs/2026-05-30-phase-1-api-contracts-design.md`
- `docs/adr/0006-api-contract-envelope-and-model-source.md`
- `docs/upbit/api/websocket/ticker.md`
- `docs/upbit/api/websocket/trade.md`
- `docs/upbit/api/websocket/orderbook.md`
- `docs/upbit/api/websocket/candle.md`
- `docs/upbit/api/quotation/candles.md`
- `docs/upbit/api/rate-limits.md`
- `docs/upbit/api/rest-api-guide.md`
- `docs/upbit/api/websocket-guide.md`

작업:

- 백엔드 `apps/backend/src/upbit_dashboard/contracts/` 패키지 추가
- REST 성공/에러 envelope Pydantic 모델 정의
- WebSocket event envelope Pydantic 모델 정의
- `ticker:update`, `trade:update`, `orderbook:update`, `candle:update`, `alert:new` 이벤트 data 모델 정의
- `markets:list`, `market-state:snapshot`, `candles:list` REST response 모델 정의
- Upbit WebSocket ticker 원본 모델 `UpbitTickerMessage` 정의
- `UpbitTickerMessage -> TickerData` mapper 정의
- 각 Pydantic 필드에 `serialization_alias`와 `description` 명시
- 프론트 `apps/web/src/lib/contracts/` TypeScript 타입 정의
- 400/422, 418/429, Upbit upstream error를 분리한 error contract 정의
- Pydantic alias, description, validation, mapper, error mapping 테스트 작성

계약 정책:

- Python 내부 필드명은 snake_case를 사용한다.
- JSON/TypeScript 필드명은 camelCase를 사용한다.
- REST 성공/실패 응답은 `type`, `timestamp`, `data` envelope를 사용한다.
- Backend -> Frontend WebSocket 이벤트도 `type`, `timestamp`, `data` envelope를 사용한다.
- Envelope의 `timestamp`는 우리 서버가 응답 또는 이벤트를 만든 시각이다.
- Upbit 원본 ms timestamp는 `timestampMs`, `tradeTimestampMs`처럼 data 내부에 보존한다.
- `/api/snapshot`의 `tickers[]`는 `ticker:update.data`와 같은 `TickerData` 구조를 사용한다.
- `/api/candles`는 `1m`, `5m`, `15m`, `30m`, `1h`, `1d`, `1w`를 지원한다.
- WebSocket `candle:update`는 `1m`, `5m`, `15m`, `30m`, `1h`만 지원한다.

완료 기준:

- 백엔드 Pydantic 계약 모델이 존재한다.
- 프론트 TypeScript 계약 타입이 존재한다.
- Upbit ticker raw 모델과 mapper가 존재한다.
- 계약 테스트가 통과한다.
- 프론트 lint/build가 통과한다.
- 실제 Upbit 연결 없이도 Phase 2에서 수신한 ticker를 `TickerData`로 변환할 준비가 끝난다.
```

- [ ] **Step 2: 전체 백엔드 테스트 실행**

Run:

```bash
rtk test make test-api
```

Expected:

```text
pytest 통과
```

- [ ] **Step 3: 프론트 lint/build 실행**

Run:

```bash
rtk test make lint-web
rtk test make build-web
```

Expected:

```text
lint 통과
build 통과
```

- [ ] **Step 4: diff whitespace 검증**

Run:

```bash
rtk git diff --check
```

Expected:

```text
출력 없음
```

- [ ] **Step 5: 최종 상태 확인**

Run:

```bash
rtk git status --short
```

Expected:

```text
Phase 1 구현 파일과 docs/development-sequence.md만 변경됨
기존 사용자 변경 파일이 있으면 그대로 남아 있음
```

- [ ] **Step 6: 단계 커밋**

Run:

```bash
rtk git add docs/development-sequence.md
rtk git commit -m "docs: update phase 1 development sequence"
```

Expected:

```text
커밋 생성
```

- [ ] **Step 7: Phase 1 구현 완료 확인**

Run:

```bash
rtk git log --oneline -6
```

Expected:

```text
docs: update phase 1 development sequence
feat: add frontend api contract types
feat: add upbit ticker contract mapper
feat: add rest response contract models
feat: add websocket event contract models
feat: add backend error contract models
```
