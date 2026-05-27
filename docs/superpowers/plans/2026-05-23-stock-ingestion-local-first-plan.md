#인수집 지역 우선 추진 신개념

> **대리인용: ** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**목표: ** Build a local-first development path that verifies schema, mock API ingestion, upsert, and rollup before hosted Supabase or Cloudflare deployment.

**건축학: ** Use Supabase local dev as the preferred environment and provide a plain Postgres fallback. Add a mock stock API fixture server and repeatable local verification commands. Git steps are intentionally omitted because the user requested no git operations.

**기술 그리드: ** Supabase CLI, Docker, Postgres SQL, TypeScript, Vitest, Cloudflare Wrangler local scheduled handler.

---

## 파일구조

-만들다: `supabase/config.toml` - local Supabase project config.
-만들다: `supabase/seed.sql` - local seed data for markets and watchlist.
-만들다: `test/fixtures/stock-api/aapl.json` - mock stock API response.
-만들다: `scripts/mock-stock-api.mjs` - local HTTP mock server.
-만들다: `scripts/run-scheduled-local.mjs` - local scheduled trigger helper.
-만들다: `docs/local-stock-ingestion-runbook.md` - local verification commands.

## 작업 1: Add Supabase Local Config

**파일: **
-만들다: `supabase/config.toml`
-만들다: `supabase/seed.sql`

- [ ] **1 단계: Supabase 위치 구성 생성**

`supabase/config.toml`을 생성합니다:

```toml
project_id = "stock-ingestion-local"

[api]
enabled = true
port = 54321
schemas = ["public"]
extra_search_path = ["public", "extensions"]
max_rows = 1000

[db]
port = 54322
major_version = 15

[studio]
enabled = true
port = 54323
```

- [ ] **2단계: 시드 데이터 생성**

`supabase/seed.sql`을 생성합니다:

```sql
insert into public.markets (code, timezone, regular_open, regular_close, enabled)
values
  ('krx', 'Asia/Seoul', '09:00', '15:30', true),
  ('us', 'America/New_York', '09:30', '16:00', true)
on conflict (code) do update set
  timezone = excluded.timezone,
  regular_open = excluded.regular_open,
  regular_close = excluded.regular_close,
  enabled = excluded.enabled;

insert into public.watchlist_symbols (symbol, market_code, source_symbol, priority, enabled)
values
  ('AAPL', 'us', 'AAPL', 1, true),
  ('MSFT', 'us', 'MSFT', 2, true),
  ('005930', 'krx', '005930', 1, true)
on conflict (market_code, symbol) do update set
  source_symbol = excluded.source_symbol,
  priority = excluded.priority,
  enabled = excluded.enabled;
```

- [ ] **3단계:위치 Supabase 시작**

나다: `rtk proxy supabase start`

예상되는: local API URL, DB URL, and service role key are printed.

## 작업 2: Add Mock Stock API

**파일: **
-만들다: `test/fixtures/stock-api/aapl.json`
-만들다: `scripts/mock-stock-api.mjs`

- [ ] **1단계: 고정 추가 장치**

`test/fixtures/stock-api/aapl.json`을 등록합니다.

```json
{
  "symbol": "AAPL",
  "timestamp": "2026-05-23T13:39:59.000Z",
  "open": 190.1,
  "high": 191.2,
  "low": 189.8,
  "close": 190.7,
  "volume": 1234567
}
```

- [ ] **2단계: 모의 서버 추가**

`scripts/mock-stock-api.mjs`를 생성합니다:

```js
import http from "node:http";
import { readFile } from "node:fs/promises";

const port = Number(process.env.MOCK_STOCK_API_PORT || 8788);

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url || "/", `http://127.0.0.1:${port}`);
  const symbol = url.searchParams.get("symbol") || "AAPL";

  if (url.pathname !== "/quote") {
    res.writeHead(404, { "content-type": "application/json" });
    res.end(JSON.stringify({ error: "not_found" }));
    return;
  }

  const body = await readFile(new URL("../test/fixtures/stock-api/aapl.json", import.meta.url), "utf8");
  const json = JSON.parse(body);
  json.symbol = symbol;
  res.writeHead(200, { "content-type": "application/json" });
  res.end(JSON.stringify(json));
});

server.listen(port, "127.0.0.1", () => {
  console.log(`mock stock api listening on http://127.0.0.1:${port}`);
});
```

- [ ] **3단계: 모의 API 확인**

나다: `rtk proxy node scripts/mock-stock-api.mjs`

예상되는: server starts and logs `mock stock api listening`.

## 작업 3: Add Local Scheduled Run Helper

**파일: **
-만들다: `scripts/run-scheduled-local.mjs`

- [ ] **1단계: 시트 확장 추가**

`scripts/run-scheduled-local.mjs`를 생성합니다:

```js
const cron = process.argv[2] || "*/10 * * * *";
const url = `http://127.0.0.1:8787/__scheduled?cron=${encodeURIComponent(cron)}`;

const response = await fetch(url);
const text = await response.text();

console.log(response.status);
console.log(text);

if (!response.ok) {
  process.exitCode = 1;
}
```

- [ ] **2단계: Wrangler 개발실행**

나다: `rtk npm run dev`

예상되는: Wrangler dev starts and exposes local Worker on port 8787.

- [ ] **3단계: 예약된 핸들러**

나다: `rtk proxy node scripts/run-scheduled-local.mjs`

예상되는: HTTP 200 from local scheduled endpoint.

## 작업 4: Write Local Runbook

**파일: **
-만들다: `docs/local-stock-ingestion-runbook.md`

- [ ] **1단계: 런북 추가**

`docs/local-stock-ingestion-runbook.md`를 등록합니다.

```md
# Local Stock Ingestion Runbook

## Start services

1. Start Supabase:
   `rtk proxy supabase start`

2. Start mock stock API:
   `rtk proxy node scripts/mock-stock-api.mjs`

3. Start Worker:
   `rtk npm run dev`

## Trigger scheduled run

Run:

`rtk proxy node scripts/run-scheduled-local.mjs`

## Verify database

Connect to local Postgres using the DB URL printed by Supabase CLI, then run:

```sql
start_at desc 제한 5를 기준으로 public.ingestion_runs 순서에서 *를 선택하세요.
public.stock_price_bars에서 *를 Interval_start desc 제한으로 주문하여 선택하세요.
```

## Stop services

Run:

`rtk proxy supabase stop`
```

- [ ] **2단계: Runbook 집합이 있는지 확인**

나다: `rtk proxy rg -n "supabase start|mock-stock-api|run-scheduled-local|stock_price_bars" docs/local-stock-ingestion-runbook.md`

예상되는: all command references are found.

## 자체인증 체크리스트

- 사양범위: local Supabase, mock API, scheduled handler, and hosted transition checks are covered.
- 아이템 열기 스캔: no unresolved design items remain.
- 일관성이 있다: local mock response fields match the `PriceBar` normalization requirements.
