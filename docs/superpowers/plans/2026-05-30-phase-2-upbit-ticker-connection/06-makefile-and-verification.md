# 06 Makefile And Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** repository root에서 Phase 2 smoke, backend dev, backend dev without Upbit, backend test를 짧은 `make` 명령으로 실행하게 한다.

**Architecture:** 기존 root `Makefile` 패턴을 유지해 `uv run --directory apps/backend ...`를 사용한다. `dev-api`와 `test-api`는 기존 타겟을 유지하고, `upbit-smoke`, `dev-api-no-upbit`을 추가한다. 마지막 검증은 자동 테스트와 make dry-run, 네트워크 smoke, FastAPI 로그 확인으로 나눈다.

**Tech Stack:** Makefile, uv, pytest, FastAPI, Upbit public API, RTK.

---

**순서:** 06 / 06
**이전 단계:** [05-fastapi-lifespan.md](./05-fastapi-lifespan.md)
**다음 단계:** 없음

### Task 06: Makefile 타겟과 Phase 2 검증

**Files:**
- Modify: `Makefile`

- [ ] **Step 1: Makefile에 Phase 2 타겟 추가**

`Makefile`의 `.PHONY`와 backend 타겟 영역을 다음 형태로 수정한다.

```makefile
.PHONY: dev dev-api dev-api-no-upbit dev-web health-api health-web test-api upbit-smoke lint-web build-web

BACKEND_HOST ?= 0.0.0.0
BACKEND_PORT ?= 8000
WEB_PORT ?= 3000
FASTAPI_BASE_URL ?= http://localhost:$(BACKEND_PORT)

dev:
	$(MAKE) -j2 dev-api dev-web

dev-api:
	uv run --directory apps/backend uvicorn upbit_dashboard.main:app --reload --host $(BACKEND_HOST) --port $(BACKEND_PORT)

dev-api-no-upbit:
	UPBIT_WS_ENABLED=false uv run --directory apps/backend uvicorn upbit_dashboard.main:app --reload --host $(BACKEND_HOST) --port $(BACKEND_PORT)

upbit-smoke:
	uv run --directory apps/backend python -m upbit_dashboard.tools.smoke_upbit_connection

dev-web:
	FASTAPI_BASE_URL=$(FASTAPI_BASE_URL) pnpm -C apps/web dev --port $(WEB_PORT)

health-api:
	curl -fsS http://localhost:$(BACKEND_PORT)/health

health-web:
	curl -fsS http://localhost:$(WEB_PORT)/api/health

test-api:
	uv run --directory apps/backend pytest

lint-web:
	pnpm -C apps/web lint

build-web:
	pnpm -C apps/web build
```

- [ ] **Step 2: Makefile dry-run 확인**

Run:

```bash
rtk proxy make -n upbit-smoke
rtk proxy make -n dev-api
rtk proxy make -n dev-api-no-upbit
rtk proxy make -n test-api
```

Expected:

```text
uv run --directory apps/backend python -m upbit_dashboard.tools.smoke_upbit_connection
uv run --directory apps/backend uvicorn upbit_dashboard.main:app --reload --host 0.0.0.0 --port 8000
UPBIT_WS_ENABLED=false uv run --directory apps/backend uvicorn upbit_dashboard.main:app --reload --host 0.0.0.0 --port 8000
uv run --directory apps/backend pytest
```

- [ ] **Step 3: 자동 테스트 실행**

Run:

```bash
rtk test make test-api
```

Expected:

```text
전체 backend 테스트 통과
```

- [ ] **Step 4: whitespace 검증**

Run:

```bash
rtk proxy git diff --check
```

Expected:

```text
출력 없음
```

- [ ] **Step 5: 실제 Upbit smoke 실행**

Run:

```bash
make upbit-smoke
```

Expected:

```text
INFO REST market check ok count=...
INFO Upbit WS connected endpoint=wss://api.upbit.com/websocket/v1
INFO ticker received market=KRW-BTC tradePrice=... streamType=...
INFO ticker received market=KRW-ETH tradePrice=... streamType=...
INFO smoke ok markets=KRW-BTC,KRW-ETH
```

- [ ] **Step 6: FastAPI 자동 연결 수동 확인**

Run:

```bash
make dev-api
```

Expected:

```text
Upbit ticker stream starting markets=KRW-BTC,KRW-ETH
Upbit ticker received market=KRW-BTC ...
Upbit ticker received market=KRW-ETH ...
```

확인 후 실행 중인 `uvicorn`을 `Ctrl-C`로 종료한다.

- [ ] **Step 7: FastAPI 자동 연결 비활성화 수동 확인**

Run:

```bash
make dev-api-no-upbit
```

Expected:

```text
Upbit ticker stream disabled by UPBIT_WS_ENABLED=false
```

다른 터미널에서 health endpoint를 확인한다.

```bash
make health-api
```

Expected:

```json
{"status":"ok","service":"upbit-dashboard-backend"}
```

확인 후 실행 중인 `uvicorn`을 `Ctrl-C`로 종료한다.

- [ ] **Step 8: 단계 커밋**

Run:

```bash
rtk proxy git add Makefile
rtk proxy git commit -m "chore: add phase 2 local make targets"
```

Expected:

```text
커밋 생성
```

- [ ] **Step 9: Phase 2 최종 상태 확인**

Run:

```bash
rtk git status
rtk proxy git log --oneline -6
```

Expected:

```text
작업트리 clean
최근 6개 커밋에 Phase 2 구현 커밋 6개가 순서대로 표시
```
