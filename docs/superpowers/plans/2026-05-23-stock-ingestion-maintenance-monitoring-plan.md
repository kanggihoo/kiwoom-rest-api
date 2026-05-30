# 재고 수집 유지 관리 및 모니터링 구현 계획

> **대리인용: ** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**목표: ** Implement pg_cron-ready rollup/delete SQL functions, maintenance run tracking, retention policies, and Grafana-friendly health views.

**건축학: ** Keep rollup and retention inside Postgres functions so they can be run manually, by pg_cron, or in tests. Record every maintenance execution in `maintenance_runs`. Git steps are intentionally omitted because the user requested no git operations.

**기술 그리드: ** PostgreSQL SQL functions, Supabase migrations, pg_cron, Grafana-ready SQL views.

---

## 파일구조

-만들다: `supabase/migrations/202605230003_stock_ingestion_rollup_functions.sql` - rollup SQL functions.
-만들다: `supabase/migrations/202605230004_stock_ingestion_retention_functions.sql` - delete/retention SQL functions.
-만들다: `supabase/migrations/202605230005_stock_ingestion_pg_cron.sql` - pg_cron schedules.
-만들다: `supabase/tests/stock_ingestion_rollup.sql` - rollup verification SQL.

## 작업 1: Add Rollup Function

**파일: **
-만들다: `supabase/migrations/202605230003_stock_ingestion_rollup_functions.sql`

- [ ] **1단계: 활성화 기능 생성**

`supabase/migrations/202605230003_stock_ingestion_rollup_functions.sql`을 생성합니다.

```sql
create or replace function public.rollup_stock_bars(
  p_market_code text,
  p_source text,
  p_target_timeframe text,
  p_from timestamptz,
  p_to timestamptz
) returns integer
language plpgsql
as $$
declare
  v_rows integer;
begin
  if p_target_timeframe not in ('30m', '1h', '1d') then
    raise exception 'unsupported target timeframe: %', p_target_timeframe;
  end if;

  with source_bars as (
    select
      source,
      market_code,
      symbol,
      session_type,
      case
        when p_target_timeframe = '30m' then to_timestamp(floor(extract(epoch from interval_start) / 1800) * 1800)
        when p_target_timeframe = '1h' then date_trunc('hour', interval_start)
        else date_trunc('day', interval_start)
      end as target_start,
      interval_start,
      open,
      high,
      low,
      close,
      volume
    from public.stock_price_bars
    where source = p_source
      and market_code = p_market_code
      and timeframe = '10m'
      and session_type = 'regular'
      and interval_start >= p_from
      and interval_start < p_to
  ),
  grouped as (
    select
      source,
      market_code,
      symbol,
      session_type,
      target_start,
      (array_agg(open order by interval_start asc))[1] as open,
      max(high) as high,
      min(low) as low,
      (array_agg(close order by interval_start desc))[1] as close,
      sum(volume) as volume,
      count(*)::integer as source_rows_count
    from source_bars
    group by source, market_code, symbol, session_type, target_start
  ),
  upserted as (
    insert into public.stock_price_bars (
      source, market_code, symbol, timeframe, interval_start, session_type,
      open, high, low, close, volume, provider_time, source_rows_count, updated_at
    )
    select
      source, market_code, symbol, p_target_timeframe, target_start, session_type,
      open, high, low, close, volume, null, source_rows_count, now()
    from grouped
    on conflict (source, market_code, symbol, timeframe, interval_start, session_type)
    do update set
      open = excluded.open,
      high = excluded.high,
      low = excluded.low,
      close = excluded.close,
      volume = excluded.volume,
      source_rows_count = excluded.source_rows_count,
      updated_at = now()
    returning 1
  )
  select count(*) into v_rows from upserted;

  insert into public.maintenance_runs (
    job_name, market_code, started_at, finished_at, status, rows_rolled_up
  ) values (
    'rollup_10m_to_' || p_target_timeframe, p_market_code, now(), now(), 'success', v_rows
  );

  return v_rows;
exception when others then
  insert into public.maintenance_runs (
    job_name, market_code, started_at, finished_at, status, error_message
  ) values (
    'rollup_10m_to_' || p_target_timeframe, p_market_code, now(), now(), 'failed', sqlerrm
  );
  raise;
end;
$$;
```

- [ ] **2단계: 마이그레이션 적용**

나다: `rtk proxy supabase db reset`

예상되는: function is created with no SQL errors.

## 작업 2: Add Retention Function

**파일: **
-만들다: `supabase/migrations/202605230004_stock_ingestion_retention_functions.sql`

- [ ] **1 연동: 저장 생성**

`supabase/migrations/202605230004_stock_ingestion_retention_functions.sql`을 생성합니다.

```sql
create or replace function public.delete_old_stock_bars(
  p_timeframe text,
  p_before timestamptz
) returns integer
language plpgsql
as $$
declare
  v_rows integer;
begin
  delete from public.stock_price_bars
  where timeframe = p_timeframe
    and interval_start < p_before;

  get diagnostics v_rows = row_count;

  insert into public.maintenance_runs (
    job_name, started_at, finished_at, status, rows_deleted
  ) values (
    'delete_old_' || p_timeframe, now(), now(), 'success', v_rows
  );

  return v_rows;
exception when others then
  insert into public.maintenance_runs (
    job_name, started_at, finished_at, status, error_message
  ) values (
    'delete_old_' || p_timeframe, now(), now(), 'failed', sqlerrm
  );
  raise;
end;
$$;
```

- [ ] **2단계: 마이그레이션 적용**

나다: `rtk proxy supabase db reset`

예상되는: retention function is created with no SQL errors.

## 작업 3: Add pg_cron Schedule Migration

**파일: **
-만들다: `supabase/migrations/202605230005_stock_ingestion_pg_cron.sql`

- [ ] **1단계: 크론 설정 생성**

`supabase/migrations/202605230005_stock_ingestion_pg_cron.sql`을 생성합니다.

```sql
create extension if not exists pg_cron with schema extensions;

select cron.schedule(
  'stock-rollup-hourly',
  '5 * * * *',
  $$
  select public.rollup_stock_bars('us', 'mock', '30m', now() - interval '3 hours', now() - interval '10 minutes');
  select public.rollup_stock_bars('us', 'mock', '1h', now() - interval '6 hours', now() - interval '10 minutes');
  select public.rollup_stock_bars('krx', 'mock', '30m', now() - interval '3 hours', now() - interval '10 minutes');
  select public.rollup_stock_bars('krx', 'mock', '1h', now() - interval '6 hours', now() - interval '10 minutes');
  $$
);

select cron.schedule(
  'stock-retention-daily',
  '30 18 * * *',
  $$
  select public.rollup_stock_bars('us', 'mock', '1d', now() - interval '7 days', now());
  select public.rollup_stock_bars('krx', 'mock', '1d', now() - interval '7 days', now());
  select public.delete_old_stock_bars('10m', now() - interval '30 days');
  select public.delete_old_stock_bars('30m', now() - interval '180 days');
  select public.delete_old_stock_bars('1h', now() - interval '730 days');
  $$
);
```

- [ ] **2단계: Supabase에서 cron 마이그레이션 적용**

나다: `rtk proxy supabase db reset`

예상되는: pg_cron extension and schedules are created. If local Postgres does not allow pg_cron, run this migration only in Supabase local/hosted, not plain Postgres fallback.

## 작업 4: Add Rollup Verification SQL

**파일: **
-만들다: `supabase/tests/stock_ingestion_rollup.sql`

- [ ] **1단계: 확인 SQL 추가**

`supabase/tests/stock_ingestion_rollup.sql`을 생성합니다.

```sql
insert into public.stock_price_bars (
  source, market_code, symbol, timeframe, interval_start, session_type,
  open, high, low, close, volume, source_rows_count
) values
  ('mock', 'us', 'AAPL', '10m', '2026-05-23T13:30:00Z', 'regular', 100, 101, 99, 100.5, 1000, 1),
  ('mock', 'us', 'AAPL', '10m', '2026-05-23T13:40:00Z', 'regular', 100.5, 102, 100, 101.5, 1100, 1),
  ('mock', 'us', 'AAPL', '10m', '2026-05-23T13:50:00Z', 'regular', 101.5, 103, 101, 102.5, 1200, 1)
on conflict (source, market_code, symbol, timeframe, interval_start, session_type)
do update set close = excluded.close;

select public.rollup_stock_bars('us', 'mock', '30m', '2026-05-23T13:30:00Z', '2026-05-23T14:00:00Z');

select
  open = 100 as open_ok,
  high = 103 as high_ok,
  low = 99 as low_ok,
  close = 102.5 as close_ok,
  volume = 3300 as volume_ok,
  source_rows_count = 3 as count_ok
from public.stock_price_bars
where source = 'mock'
  and market_code = 'us'
  and symbol = 'AAPL'
  and timeframe = '30m'
  and interval_start = '2026-05-23T13:30:00Z';
```

- [ ] **2단계: 확인 실행**

나다: `rtk proxy psql "$DATABASE_URL" -f supabase/tests/stock_ingestion_rollup.sql`

예상되는: all `_ok` columns return `t`.

## 자체인증 체크리스트

- 사양범위: 10m to 30m/1h/1d rollup, retention delete, maintenance_runs, and Grafana-ready health source tables are covered.
- 아이템 열기 스캔: no unresolved design items remain.
- 일관성이 있다: timeframe values match `stock_price_bars` check constraints and `src/types.ts`.
