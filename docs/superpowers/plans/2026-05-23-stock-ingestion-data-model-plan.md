# 주식 수집 데이터 형태를 계획하다

> **대리인용: ** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. 단계s use checkbox (`- [ ]`) syntax for tracking.

**목표: ** Implement the Supabase/Postgres schema for markets, watchlist symbols, price bars, ingestion status, maintenance status, and health views.

**아키텍처: ** Use SQL migrations with explicit constraints and indexes. Store all price timeframes in `stock_price_bars` and separate operational status into ingestion and maintenance tables. Git steps are intentionally omitted because the user requested no git operations.

**기술 그리드: ** Supabase migrations, PostgreSQL, pgTAP-style SQL checks or direct psql verification.

---

## 파일구조

- 생성: `supabase/migrations/202605230001_stock_ingestion_schema.sql` - base schema.
- 생성: `supabase/migrations/202605230002_stock_ingestion_health_views.sql` - monitoring views.
- 생성: `supabase/tests/stock_ingestion_schema.sql` - SQL verification checks.

## 작업 1: Create Base Schema Migration

**파일: **
- 생성: `supabase/migrations/202605230001_stock_ingestion_schema.sql`

- [ ] **단계 1: 마이그레이션 추가**

`supabase/migrations/202605230001_stock_ingestion_schema.sql`을 생성합니다.

```sql
create table if not exists public.markets (
  code text primary key,
  timezone text not null,
  regular_open time not null,
  regular_close time not null,
  enabled boolean not null default true
);

create table if not exists public.watchlist_symbols (
  symbol text not null,
  market_code text not null references public.markets(code),
  source_symbol text not null,
  priority integer not null,
  enabled boolean not null default true,
  last_success_at timestamptz,
  last_error_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (market_code, symbol)
);

create table if not exists public.stock_price_bars (
  id bigserial primary key,
  source text not null,
  market_code text not null references public.markets(code),
  symbol text not null,
  timeframe text not null check (timeframe in ('10m', '30m', '1h', '1d')),
  interval_start timestamptz not null,
  session_type text not null check (session_type in ('regular', 'pre_market', 'after_hours')),
  open numeric(20, 8) not null,
  high numeric(20, 8) not null,
  low numeric(20, 8) not null,
  close numeric(20, 8) not null,
  volume numeric(24, 4) not null,
  provider_time timestamptz,
  source_rows_count integer not null default 1,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint stock_price_bars_unique unique (source, market_code, symbol, timeframe, interval_start, session_type),
  constraint stock_price_bars_ohlc_check check (high >= low and high >= open and high >= close and low <= open and low <= close),
  constraint stock_price_bars_volume_check check (volume >= 0),
  constraint stock_price_bars_source_rows_check check (source_rows_count > 0)
);

create index if not exists stock_price_bars_lookup_idx
  on public.stock_price_bars (market_code, symbol, timeframe, interval_start desc);

create index if not exists stock_price_bars_retention_idx
  on public.stock_price_bars (timeframe, interval_start);

create table if not exists public.ingestion_runs (
  run_id uuid primary key default gen_random_uuid(),
  scheduled_for timestamptz not null,
  market_code text references public.markets(code),
  status text not null check (status in ('success', 'partial_success', 'failed', 'skipped_market_closed')),
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  subrequest_budget integer not null default 45,
  symbols_planned integer not null default 0,
  symbols_attempted integer not null default 0,
  symbols_succeeded integer not null default 0,
  symbols_failed integer not null default 0,
  error_message text
);

create table if not exists public.ingestion_symbol_results (
  id bigserial primary key,
  run_id uuid not null references public.ingestion_runs(run_id) on delete cascade,
  symbol text not null,
  market_code text not null references public.markets(code),
  status text not null check (status in ('success', 'failed', 'skipped_budget')),
  api_status integer,
  interval_start timestamptz,
  error_message text,
  created_at timestamptz not null default now()
);

create index if not exists ingestion_symbol_results_run_idx
  on public.ingestion_symbol_results (run_id);

create index if not exists ingestion_symbol_results_symbol_idx
  on public.ingestion_symbol_results (market_code, symbol, created_at desc);

create table if not exists public.maintenance_runs (
  id bigserial primary key,
  job_name text not null,
  market_code text references public.markets(code),
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  status text not null check (status in ('success', 'failed')),
  rows_rolled_up integer not null default 0,
  rows_deleted integer not null default 0,
  error_message text
);
```

- [ ] **단계 2: 위치로 적용 마이그레이션**

실행: `rtk proxy supabase db reset`

예상 결과: migration applies and seed data loads without SQL errors.

## 작업 2: Create Health Views

**파일: **
- 생성: `supabase/migrations/202605230002_stock_ingestion_health_views.sql`

- [ ] **단계 1: 상태 보기 추가**

`supabase/migrations/202605230002_stock_ingestion_health_views.sql`을 생성합니다.

```sql
create or replace view public.v_ingestion_health as
select
  market_code,
  max(finished_at) filter (where status in ('success', 'partial_success')) as last_success_at,
  max(finished_at) filter (where status = 'failed') as last_failed_at,
  count(*) filter (where started_at >= now() - interval '24 hours' and status = 'success')::numeric
    / nullif(count(*) filter (where started_at >= now() - interval '24 hours' and status <> 'skipped_market_closed'), 0) as success_rate_24h,
  count(*) filter (where started_at >= now() - interval '24 hours' and status = 'partial_success') as partial_success_count_24h,
  count(*) filter (where started_at >= now() - interval '24 hours' and status = 'failed') as failed_count_24h
from public.ingestion_runs
group by market_code;

create or replace view public.v_symbol_health as
select
  w.market_code,
  w.symbol,
  w.priority,
  w.last_success_at,
  w.last_error_at,
  count(r.*) filter (where r.created_at >= now() - interval '24 hours' and r.status = 'failed') as failed_count_24h
from public.watchlist_symbols w
left join public.ingestion_symbol_results r
  on r.market_code = w.market_code
 and r.symbol = w.symbol
group by w.market_code, w.symbol, w.priority, w.last_success_at, w.last_error_at;

create or replace view public.v_maintenance_health as
select
  job_name,
  market_code,
  max(finished_at) filter (where status = 'success') as last_success_at,
  max(finished_at) filter (where status = 'failed') as last_failed_at,
  sum(rows_rolled_up) filter (where started_at >= now() - interval '24 hours') as rows_rolled_up_24h,
  sum(rows_deleted) filter (where started_at >= now() - interval '24 hours') as rows_deleted_24h
from public.maintenance_runs
group by job_name, market_code;
```

- [ ] **단계 2: 마이그레이션 적용**

실행: `rtk proxy supabase db reset`

예상 결과: migrations and seed complete with no SQL errors.

## 작업 3: Add SQL Verification

**파일: **
- 생성: `supabase/tests/stock_ingestion_schema.sql`

- [ ] **작업 1: 검증 SQL 추가**

`supabase/tests/stock_ingestion_schema.sql`을 생성합니다.

```sql
insert into public.stock_price_bars (
  source, market_code, symbol, timeframe, interval_start, session_type,
  open, high, low, close, volume, provider_time, source_rows_count
) values (
  'mock', 'us', 'AAPL', '10m', '2026-05-23T13:30:00Z', 'regular',
  100, 101, 99, 100.5, 1000, '2026-05-23T13:39:59Z', 1
)
on conflict (source, market_code, symbol, timeframe, interval_start, session_type)
do update set
  open = excluded.open,
  high = excluded.high,
  low = excluded.low,
  close = excluded.close,
  volume = excluded.volume,
  updated_at = now();

select count(*) = 1 as one_aapl_bar
from public.stock_price_bars
where source = 'mock'
  and market_code = 'us'
  and symbol = 'AAPL'
  and timeframe = '10m'
  and interval_start = '2026-05-23T13:30:00Z';
```

- [ ] **작업 2: 검증 SQL 실행**

실행: `rtk proxy psql "$DATABASE_URL" -f supabase/tests/stock_ingestion_schema.sql`

예상 결과: query returns `one_aapl_bar | t`.

##인증활성화리스트

- 사양범위: all proposed tables, relationships, constraints, indexes, and health views are covered.
- 아이템 열기 스캔: no unresolved design items remain.
- 일관성이 있다: SQL values match TypeScript unions in `src/types.ts`.
