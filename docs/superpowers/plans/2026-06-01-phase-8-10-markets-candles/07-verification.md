# 07 Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Phase 8/10 REST flow가 backend와 BFF에서 전체적으로 동작하는지 자동 검증하고, spec 대비 누락이 없는지 확인한다.

**Architecture:** 이 단계는 기능 코드를 추가하지 않는다. Backend pytest, frontend Vitest/lint/build, route 검색, whitespace check를 실행하고 실패가 있으면 해당 단계 문서로 돌아가 수정한다.

**Tech Stack:** pytest, Vitest, ESLint, Next build, git diff, RTK.

---

**순서:** 07 / 07  
**이전 단계:** [06-next-bff-routes.md](./06-next-bff-routes.md)  
**다음 단계:** 없음

### Task 01: backend 전체 테스트

**Files:**
- Verify: `apps/backend/tests`

- [ ] **Step 1: backend pytest 실행**

Run:

```bash
rtk test uv run --directory apps/backend pytest -q
```

Expected:

```text
전체 backend tests passed
```

- [ ] **Step 2: 핵심 route와 helper 검색**

Run:

```bash
rtk proxy rg -n "get_markets|get_candles|MarketCatalogueService|build_candle_path|resolve_ticker_markets|RequestValidationError" apps/backend/src/upbit_dashboard apps/backend/tests
```

Expected:

```text
markets route, candles route, market catalogue service, candle path mapping, ticker market resolver, validation handler 검색 결과 확인
```

### Task 02: frontend BFF 테스트와 build

**Files:**
- Verify: `apps/web/src/app/api/markets/route.ts`
- Verify: `apps/web/src/app/api/candles/route.ts`
- Verify: `apps/web/tests/bff`

- [ ] **Step 1: frontend Vitest 실행**

Run:

```bash
rtk test pnpm --dir apps/web test
```

Expected:

```text
전체 frontend tests passed
```

- [ ] **Step 2: frontend lint 실행**

Run:

```bash
rtk test pnpm --dir apps/web lint
```

Expected:

```text
lint 통과
```

- [ ] **Step 3: frontend build 실행**

Run:

```bash
rtk test pnpm --dir apps/web build
```

Expected:

```text
Next.js build 통과
```

### Task 03: spec coverage self-check

**Files:**
- Verify: `docs/superpowers/specs/2026-06-01-phase-8-10-markets-candles-design.md`
- Verify: `docs/superpowers/plans/2026-06-01-phase-8-10-markets-candles`

- [ ] **Step 1: spec 요구사항 검색 확인**

Run:

```bash
rtk proxy rg -n "10분|stale|count|to|1h|오름차순|RequestValidationError|BFF|all_krw" docs/superpowers/specs/2026-06-01-phase-8-10-markets-candles-design.md docs/superpowers/plans/2026-06-01-phase-8-10-markets-candles apps/backend/src/upbit_dashboard apps/web/src/app/api apps/backend/tests apps/web/tests
```

Expected:

```text
각 spec 핵심 정책이 plan, source, tests 중 하나 이상에서 확인됨
```

- [ ] **Step 2: whitespace check**

Run:

```bash
rtk proxy git diff --check
```

Expected:

```text
출력 없음
```

- [ ] **Step 3: 최종 커밋**

Run:

```bash
rtk proxy git status --short
rtk proxy git add apps/backend apps/web docs/superpowers/plans/2026-06-01-phase-8-10-markets-candles
rtk proxy git commit -m "test: verify markets and candles rest flow"
```

Expected:

```text
검증 수정이 있었으면 커밋 생성
변경 사항이 없으면 git이 nothing to commit을 출력
```

### Task 04: 선택 수동 검증

**Files:**
- Verify: running backend process

- [ ] **Step 1: backend를 Upbit WS 없이 실행**

Run:

```bash
cd apps/backend
UPBIT_WS_ENABLED=false uv run uvicorn upbit_dashboard.main:app --host 127.0.0.1 --port 8000
```

Expected:

```text
Uvicorn running on http://127.0.0.1:8000
```

- [ ] **Step 2: `/api/markets` 수동 호출**

다른 terminal에서 실행한다.

```bash
curl -s 'http://127.0.0.1:8000/api/markets' | python -m json.tool | head -40
```

Expected:

```text
"type": "markets:list"
"market": "KRW-BTC" 같은 KRW Market 포함
```

- [ ] **Step 3: `/api/candles` 수동 호출**

```bash
curl -s 'http://127.0.0.1:8000/api/candles?market=KRW-BTC&unit=1m&count=3' | python -m json.tool
```

Expected:

```text
"type": "candles:list"
"candleUnit": "1m"
"candles" 배열 길이 최대 3
```

- [ ] **Step 4: 단계 커밋**

수동 검증 중 문서나 코드 수정이 없다면 커밋하지 않는다. 수정이 있었다면 다음을 실행한다.

```bash
rtk proxy git status --short
rtk proxy git add apps/backend apps/web docs/superpowers/plans/2026-06-01-phase-8-10-markets-candles
rtk proxy git commit -m "test: verify markets and candles rest flow"
```
