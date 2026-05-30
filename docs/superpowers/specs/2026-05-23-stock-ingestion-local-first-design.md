# 재고 수집 지역 우선 설계

작성일: 2026-05-23

## 목적

Hosted Supabase와 Cloudflare Worker에 바로 배포하지 않고, 장소에서 스키마, upsert, 롤업, 보존, 작업자 수집을 샘플로 검증합니다. 주장이 반복 가능해지면 Supabase와 Cloudflare 개발 환경으로 이동해야 합니다.

## 단계

```txt
Phase 1. Local-only prototype
Phase 2. Hosted Supabase dry run
Phase 3. Cloudflare Worker dev
Phase 4. Production free-plan run
```

## 1단계: Local-only prototype

기본 선택은 Supabase local dev다. Supabase CLI와 Docker로 배치 Supabase stack을 띄우고, 마이그레이션과 SQL 함수를 모형에서 검증합니다. Docker 구성이 필요하기 때문에 plain local Postgres로 DDL, upsert, Rollup SQL만 먼저 검증할 수 있습니다.

검증 범위:

- `markets`, `watchlist_symbols`, `stock_price_bars`, `ingestion_runs`, `ingestion_symbol_results`, `maintenance_runs` DDL.
- `stock_price_bars` 고유 키와 upsert.
- 10분봉에서 30분봉, 1시간봉, 일봉 SQL을 생성합니다.
- 기간별 보존 SQL을 삭제합니다.
- 모의주식 API 응답을 OHLCV로 표준화합니다.
- 예약된 핸들러를 수동으로 실행하는 테스트 하네스입니다.
- 실패 응답, 시간 초과, 잘못된 페이로드에 대한 상태 기록.

전면 재고 API는 처음에는 모의 서버 또는 고정 장치 JSON으로 죽다. 실제 API는 스키마와 속도 제한을 믿고 작은 기호 집합으로만 붙인다.

## 2단계: Hosted Supabase dry run

Hosted Supabase Free 프로젝트에 스키마를 적용하고 3~5개 기호만 대상으로 수동 수집을 실행합니다.

검증 범위:

- Supabase REST API 또는 `supabase-js` 일괄 upsert.
- 비밀 키가 코드와 config에 남지 않는지.
- `ingestion_runs`와 `ingestion_symbol_results` 기록.
- pg_cron job 또는 수동 SQL로 롤업/삭제 실행.
- Supabase 대시보드에서 DB 크기와 로그 확인.

## 3단계: Cloudflare Worker dev

`wrangler dev --test-scheduled`와 `/__scheduled?cron=...`로 예약된 핸들러를 호출합니다. 이 단계에서는 Supabase를 저장합니다.

검증 범위:

- Cron 핸들러가 시장 세션을 정확하게 이해합니다.
- 하위 요청 예산 집적은 50개의 외부 하위 요청을 초과하지 않습니다.
- 우선순위 기반 기호가 예측대로 동작하는지 확인합니다.
- 부분적인 실패가 상태로 남아있습니다.
- KV 커서/상태 저장이 실패해도 DB upsert가 깨지지 않습니다.

## 4단계: Production free-plan run

Cloudflare Cron Trigger를 10분으로 배포합니다. 초기에는 40~50개보다 작은 기호로 시작하고, 성공률과 할당량을 구별할 수 없을린다.

운영 전 체크리스트:

- 모든 비밀은 Cloudflare 비밀 또는 Supabase 보안 설정에만 있습니다.
- Worker config의 `vars`에는 비민감 값만 있습니다.
- `watchlist_symbols.priority`가 방향으로 방향을 바꾸게 됩니다.
- `ingestion_runs` 이후 결과가 성공 또는 부분 성공으로 남아있습니다.
- 롤업/삭제 작업이 로컬과 호스팅에서 한 번 이상 성공했습니다.
- DB 크기를 SQL 또는 Grafana 패널이 준비되어 있습니다.

## 호스팅 전환 기준

다음 조건이 만족스러우면 호스팅된 Supabase dry run으로 할까요.

- Fixture로 여러 번 실행해도 `stock_price_bars` 유사 row가 인스턴스입니다.
- 유효하지 않은 API 페이로드가 가격표에 들어가지 않습니다.
- 롤업 SQL과 동일한 기간을 여러 번 실행해도 동일한 결과로 upsert가 됩니다.
- 보존 삭제 대상 기간만 삭제합니다.
- 상태 테이블에 성공, 부분 성공, 실패가 분리되어 있습니다.
