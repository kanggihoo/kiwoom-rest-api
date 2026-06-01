# Phase 8/10 Markets and Candles REST API Implementation Plan Index

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** FastAPI backend와 Next.js BFF에 `GET /api/markets`, `GET /api/candles`를 추가하고, backend가 전체 KRW Market 목록을 재사용해 Phase 8 ticker 확장과 Phase 10 candle history 조회를 지원하게 만든다.

**Architecture:** FastAPI가 Upbit Quotation REST adapter, error mapping, Market metadata cache, candle mapping의 소유자가 된다. `/api/markets`는 10분 process-memory cache와 stale-on-error 정책을 사용하고, `/api/candles`는 요청마다 Upbit candle REST를 호출해 오름차순 candle list로 변환한다. Next.js BFF는 cache/revalidation 없이 FastAPI REST 응답을 같은 origin으로 전달한다.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, httpx, pytest, Next.js Route Handlers, TypeScript, Vitest, pnpm, uv, RTK.

---

## 기준 스펙

- [Phase 8/10 Markets and Candles REST API 설계](../../specs/2026-06-01-phase-8-10-markets-candles-design.md)

## 실행 순서

| 순번 | 문서 | 산출물 | 커밋 메시지 |
| --- | --- | --- | --- |
| 01 | [01-upbit-rest-adapter.md](./01-upbit-rest-adapter.md) | Upbit REST client, raw model, error mapping, `httpx` runtime dependency | `feat: add upbit quotation rest adapter` |
| 02 | [02-market-catalogue-route.md](./02-market-catalogue-route.md) | `MarketCatalogueService`, 10분 cache, `GET /api/markets` | `feat: expose krw market catalogue` |
| 03 | [03-candles-route.md](./03-candles-route.md) | candle unit mapping, query validation, `GET /api/candles` | `feat: expose candle history endpoint` |
| 04 | [04-validation-error-envelope.md](./04-validation-error-envelope.md) | FastAPI validation error envelope와 Upbit error route 회귀 테스트 | `feat: normalize backend rest validation errors` |
| 05 | [05-all-krw-ticker-wiring.md](./05-all-krw-ticker-wiring.md) | 전체 KRW ticker subscription startup wiring과 설정 | `feat: support all krw ticker subscriptions` |
| 06 | [06-next-bff-routes.md](./06-next-bff-routes.md) | Next.js `/api/markets`, `/api/candles` BFF Route Handler와 Vitest | `feat: add markets and candles bff routes` |
| 07 | [07-verification.md](./07-verification.md) | backend/frontend 전체 검증, 문서 self-check | `test: verify markets and candles rest flow` |

## 전체 파일 구조

### Backend source

```text
apps/backend/pyproject.toml
apps/backend/src/upbit_dashboard/api/exception_handlers.py
apps/backend/src/upbit_dashboard/api/router.py
apps/backend/src/upbit_dashboard/api/routes/markets.py
apps/backend/src/upbit_dashboard/api/routes/candles.py
apps/backend/src/upbit_dashboard/market/catalogue.py
apps/backend/src/upbit_dashboard/settings.py
apps/backend/src/upbit_dashboard/main.py
apps/backend/src/upbit_dashboard/upbit/rest.py
```

### Backend tests

```text
apps/backend/tests/conftest.py
apps/backend/tests/test_exception_handlers.py
apps/backend/tests/test_market_catalogue.py
apps/backend/tests/test_markets_route.py
apps/backend/tests/test_candles_route.py
apps/backend/tests/test_upbit_rest.py
apps/backend/tests/test_upbit_runner.py
apps/backend/tests/test_lifespan.py
apps/backend/tests/test_settings.py
```

### Frontend source

```text
apps/web/src/app/api/markets/route.ts
apps/web/src/app/api/candles/route.ts
```

### Frontend tests

```text
apps/web/tests/bff/markets-route.test.ts
apps/web/tests/bff/candles-route.test.ts
```

## 전체 검증 명령

모든 단계가 끝나면 repository root에서 실행한다.

```bash
rtk test uv run --directory apps/backend pytest -q
rtk test pnpm --dir apps/web test
rtk test pnpm --dir apps/web lint
rtk test pnpm --dir apps/web build
rtk proxy git diff --check
```

예상 결과:

```text
backend pytest 통과
frontend vitest 통과
frontend lint 통과
frontend build 통과
diff whitespace check 통과
```

선택 수동 검증:

```bash
UPBIT_WS_ENABLED=false uv run --directory apps/backend uvicorn upbit_dashboard.main:app --host 127.0.0.1 --port 8000
curl -s 'http://127.0.0.1:8000/api/markets'
curl -s 'http://127.0.0.1:8000/api/candles?market=KRW-BTC&unit=1m&count=3'
```

## 실행 원칙

- 각 단계는 번호 순서대로 실행한다.
- 각 단계는 테스트를 먼저 작성하고 실패를 확인한다.
- 단계별 커밋을 만든다.
- 자동 테스트는 Upbit 네트워크에 연결하지 않는다.
- `/api/markets` cache는 FastAPI process memory에만 둔다.
- Next.js BFF에는 `revalidate`나 route-level cache를 추가하지 않는다.
- `/api/candles` 응답은 backend state에 저장하지 않는다.
- `1h`는 frontend/backend 앱 계약이고 Upbit REST 호출에서만 `minutes/60`으로 매핑한다.
- `to`는 해당 시각 이전 candle을 조회하는 pagination 기준이다.

## 계획 자체 검토

- Spec coverage: `/api/markets`, 10분 cache, stale-on-error, `/api/candles`, count/to 정책, candle unit mapping, error envelope, BFF route, 전체 KRW ticker service 재사용이 단계별 문서에 매핑되어 있다.
- Placeholder scan: plan-writing checklist의 금지 placeholder 없이 파일 경로, 테스트 이름, 구현 함수, 검증 명령을 명시했다.
- Type consistency: `MarketSummary`, `MarketsListResponse`, `Candle`, `CandlesListResponse`, `CandleUnit`, `DashboardApiError`, `RestErrorCode` 이름은 현재 backend 계약과 일치한다.
