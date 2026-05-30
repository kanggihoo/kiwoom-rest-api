# 재고 수집 유지 관리 및 모니터링 설계

작성일: 2026-05-23

## 목적

Supabase pg_cron으로 낮은 시간대 데이터를 상위 답변으로 롤업하고 오래된 데이터를 삭제합니다. 상태 테이블과 health view를 기반으로 Grafana 캐스팅을 준비한다. 알림은 확장형으로 확장됩니다.

## 롤업 원칙

노동자는 `10m`만 절약한다. 상위 레벨은 Supabase Postgres에서 생성합니다.

```txt
10m -> 30m
10m -> 1h
10m -> 1d
```

상위 위치는 `stock_price_bars`와 같은 테이블에 다른 `timeframe` 값으로 upsert됩니다.

## OHLCV에 대해

하위 봉에서 상위 봉을 만들 때 다음 규칙을 사용합니다.

```txt
open   = 상위 구간 안 첫 하위 봉의 open
high   = max(high)
low    = min(low)
close  = 상위 구간 안 마지막 하위 봉의 close
volume = sum(volume)
source_rows_count = 사용한 하위 봉 개수
```

기분은 `session_type = 'regular'`로 활동합니다. 원래에는 시간외 데이터를 수집하지 않는다는 것이다.

##만들기만 하면 된다

진행중인 프로세스는 롤업되지 않는다는 것입니다. 예를 들어 현재 시간이 10: 42이면 10:40~10:50 구간은 아직 완료되지 않았으므로 상위 봉 집계에서 제외한다.

인덱스 10분봉을 보정하기 위해 롤업 작업은 최근 기간을 반복적으로 upsert합니다. 예를 들어 30분봉과 1시간봉은 앞으로 2~3시간, 일봉은 앞으로 3거래일을 재계산할 수 있습니다.

## 일일 롤업

일봉은 시장 시간대 기준 거래일로 계산합니다. UTC 데이트로 인해 미장 데이터가 잘못된 거래일에 들어갈 수 있습니다.

일봉은 장탄력으로 전설을 실행합니다. DST가 있는 미장 고정 UTC cron은 전적으로 어긋날 수 있고, 서식지 방식은 매시간 유지 관리 디스패처를 실행하고 SQL 내부에서 시장별 현지 시간과 마지막 롤업 여부에 관계하는 것입니다.

## 보존

초기 보관상태:

```txt
10m: 30일
30m: 180일
1h: 1~2년
1d: 장기 보관
```

Supabase Free DB 포이 80%에 가까워지면 이동 전환 대신 보관 기간을 줄인다.

삭제하는 기간을 수행합니다.

```txt
delete stock_price_bars
where timeframe = '10m'
  and interval_start < now() - interval '30 days';
```

도매 삭제는 DB bloat를 만들 수 있는 상당히 작은 배치 삭제 또는 진공 상태를 확인합니다. 초기 규모에서는 삭제로 시작됩니다.

## 유지 관리 실행

모든 유지 관리 작업은 `maintenance_runs`에 기록됩니다.

기록 대상:

- `rollup_10m_to_30m`
- `rollup_10m_to_1h`
-`rollup_10m_to_1d`
- `delete_old_bars`

각 실행은 `market_code`, `status`, `rows_rolled_up`, `rows_deleted`, `error_message`를 남다.

## 모니터링 레이어

모델은 세 층으로 다.

```txt
Application health: Supabase 상태 테이블과 view
Database health: Supabase Metrics API -> Grafana
Worker health: Cloudflare Workers OTel/Logs -> Grafana
```

초기에는 상태와 테이블 SQL 뷰만으로 운영을 확인할 수 있어야 합니다.

## 그라파나 패널

나중에 Grafana를 연결하면 다음 패널을 구성합니다.

```txt
최근 24시간 ingestion success rate
시장별 마지막 성공 시각
실패 종목 Top N
API status 분포
수집된 10m bar 개수
rollup 성공/실패 이력
rows_deleted 추이
DB size 추이
DB connection 수
Worker error count
Worker execution duration
```

## 건강 뷰

Grafana와 SQL 작업을 위해 다음 뷰를 죽입니다.

`v_ingestion_health`:

```txt
market_code
last_success_at
last_failed_at
success_rate_24h
partial_success_count_24h
failed_count_24h
```

`v_symbol_health`:

```txt
market_code
symbol
priority
last_success_at
last_error_at
failed_count_24h
```

`v_maintenance_health`:

```txt
job_name
market_code
last_success_at
last_failed_at
rows_rolled_up_24h
rows_deleted_24h
```

## 향후 알림

알림은 매듭이 있습니다. 기준은 미리 정해두지 마세요.

- 정규장인데 30분 이상 성공이 없습니다.
- 특정 우선순위가 높은 30분 이상 수집이 실패했습니다.
- Rollup이 하루 이상 실패했습니다.
- DB 크기가 무료 한도가 80% 이상이다.
- API 429 능력이 강화되었습니다.

알림 구현은 Discord, Slack, 이메일 중 하나를 선택해 Cloudflare Worker 또는 Supabase Edge Function에서 처리합니다.
