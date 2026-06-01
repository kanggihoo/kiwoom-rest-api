# 04 Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Phase 3 구현 전체가 backend 테스트와 수동 검증 기준을 만족하는지 확인한다.

**Architecture:** 자동 검증은 pytest, route/wiring 검색, whitespace check로 끝낸다. Upbit 네트워크를 쓰는 검증은 선택 수동 단계로 분리해 local environment에서만 실행한다.

**Tech Stack:** pytest, FastAPI, curl, Makefile, RTK.

---

**순서:** 04 / 04
**이전 단계:** [03-market-state-semantics.md](./03-market-state-semantics.md)
**다음 단계:** 없음

### Task 04: Phase 3 전체 검증

**Files:**
- Verify: `apps/backend/src/upbit_dashboard/api/router.py`
- Verify: `apps/backend/src/upbit_dashboard/api/routes/snapshot.py`
- Verify: `apps/backend/src/upbit_dashboard/main.py`
- Verify: `apps/backend/tests/test_snapshot.py`
- Verify: `apps/backend/tests/test_lifespan.py`
- Verify: `apps/backend/tests/test_market_state.py`

- [ ] **Step 1: backend 전체 테스트 실행**

Run:

```bash
rtk test uv run --directory apps/backend pytest -q
```

Expected:

```text
전체 backend 테스트 통과
```

- [ ] **Step 2: route 등록과 ticker handler wiring 확인**

Run:

```bash
rtk proxy rg -n "get_snapshot|/api/snapshot|on_ticker|handle_ticker|log_ticker" apps/backend/src/upbit_dashboard apps/backend/tests
```

Expected:

```text
apps/backend/src/upbit_dashboard/api/routes/snapshot.py
apps/backend/src/upbit_dashboard/api/router.py
apps/backend/src/upbit_dashboard/main.py
apps/backend/tests/test_snapshot.py
apps/backend/tests/test_lifespan.py
```

- [ ] **Step 3: whitespace 검증**

Run:

```bash
rtk git diff --check
```

Expected:

```text
출력 없음
```

- [ ] **Step 4: 구현 diff 검토**

Run:

```bash
rtk git diff --stat
rtk git diff -- apps/backend/src/upbit_dashboard/api apps/backend/src/upbit_dashboard/main.py apps/backend/tests/test_lifespan.py apps/backend/tests/test_market_state.py apps/backend/tests/test_snapshot.py
```

Expected:

```text
snapshot.py는 MarketState를 읽고 MarketStateSnapshotResponse를 반환한다.
router.py는 snapshot router를 등록한다.
main.py는 run_ticker_stream()에 on_ticker를 넘긴다.
handle_ticker()는 app.state.market_state를 업데이트하고 log_ticker()를 호출한다.
tests는 Upbit 네트워크에 연결하지 않는다.
```

- [ ] **Step 5: Upbit 비활성화 상태에서 snapshot 수동 확인**

Run server in one terminal:

```bash
make dev-api-no-upbit
```

Run in another terminal:

```bash
curl -s http://localhost:8000/api/snapshot
```

Expected response shape:

```json
{
  "type": "market-state:snapshot",
  "timestamp": "...",
  "data": {
    "generatedAt": "...",
    "tickers": []
  }
}
```

확인 후 실행 중인 `uvicorn`을 `Ctrl-C`로 종료한다.

- [ ] **Step 6: Upbit 활성화 상태에서 ticker 저장 수동 확인**

Run server in one terminal:

```bash
make dev-api
```

After ticker logs appear, run in another terminal:

```bash
curl -s http://localhost:8000/api/snapshot
```

Expected:

```text
Response type is market-state:snapshot.
data.tickers contains KRW-BTC or KRW-ETH after ticker messages arrive.
Backend logs still include "Upbit ticker received ...".
```

확인 후 실행 중인 `uvicorn`을 `Ctrl-C`로 종료한다.

- [ ] **Step 7: 최종 커밋**

Tasks 01-03에서 단계별 커밋을 만들지 않았다면 전체 변경을 한 번에 커밋한다.

```bash
rtk proxy git add apps/backend/src/upbit_dashboard/api/router.py apps/backend/src/upbit_dashboard/api/routes/snapshot.py apps/backend/src/upbit_dashboard/main.py apps/backend/tests/test_lifespan.py apps/backend/tests/test_market_state.py apps/backend/tests/test_snapshot.py
rtk proxy git commit -m "feat: add backend market state snapshot"
```

Expected:

```text
커밋 생성
```

- [ ] **Step 8: Phase 3 최종 상태 확인**

Run:

```bash
rtk git status
rtk proxy git log --oneline -4
```

Expected:

```text
작업트리 clean
최근 4개 커밋에 Phase 3 구현 커밋이 순서대로 표시
```
