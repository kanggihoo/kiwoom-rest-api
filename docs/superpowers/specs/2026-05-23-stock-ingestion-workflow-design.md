# 재고 수집 워크플로우 설계

작성일: 2026-05-23

## 목적

Cloudflare Cron Worker는 무료 계획 할당량을 대용량지 서버 정규화 중 일부를 OHLCV를 수집하고 Supabase에 저장하는 간단한 실행을 정의합니다.

## 크론 실행

Cron Trigger는 10마다 실행한다. Cron은 UTC 기준으로 동작하지만, Worker 내부에서 시장 시간대로 변환해 범위의 여부를 결정합니다.

```txt
*/10 * * * *
```

Worker가 실행하는 다음 순서대로 동작합니다.

1. 현재 UTC를 기준으로 시장별 현지 시간을 계산한다.
2. `시장`에서 활성화된 시장을 조회한다.
3. 교정장인 시장만 수집 대상으로 죽다.
4. 표시 시장이 없으면 `skipped_market_closed` 실행을 기록하고 종료합니다.
5. 공개 시장의 'watchlist_symbols'를 우선순위로 오름차순으로 조회합니다.
6. 하위 요청 예산을 처리하는 데 사용할 수 있습니다.
7. 우선 순위가 높은 외부 주식 API를 호출합니다.
8. 성공 응답을 `stock_price_bars(timeframe='10m')` row로 정규화한다.
9. 성공 행을 Supabase에 일괄 upsert한다.
10. 결과와 쿼리별 결과를 기록합니다.
11. `watchlist_symbols.last_success_at` 또는 `last_error_at`을 기대한다.
12. KV에 마지막 실행상태를 요약하여 저장한다.

## 하위 요청 예산

Cloudflare 무료 요금제에서 외부 하위 요청은 한 호출당 50개로 봅니다. Supabase REST API 호출도 외부 하위 요청으로 취소합니다.

경화적 예산:

```txt
total limit: 50
reserved:
  watchlist 조회: 1
  price batch upsert: 1
  run/result 기록: 1~2
  watchlist 상태 갱신: 1
  KV/status 여유: 1
  safety margin: 2~3

stock API budget: 약 43~45 symbols
```

초기에 집중이 40~50개라도 모든 곡선을 받고 있다고 가정합니다. 우선순위가 높은 것부터 예산 내에서 처리한다.

## 우선 정책

쿠션 우선순위를 따릅니다.

```txt
order by priority asc, symbol asc
limit stock_api_budget
```

우선 순위가 낮은 밀릴 수 있습니다. 조심해야 합니다. 무료 할당량을 초과하지 않는 것이 최신보다 우선적입니다.

## 간격 계산

수집 기간은 `10m`다. 작업자는 현재 시간을 시장 시간대 기준으로 10분 단위로 진행됩니다.

예:

```txt
09:32 -> interval_start 09:30
09:40 -> interval_start 09:40
09:49 -> interval_start 09:40
```

본질적으로 실질적으로 활용을 저장하는 것입니다. 예를 들어 09: 40에 실행된 run은 09:30~09:40 구간을 `interval_start = 09:30`으로 저장한다. 진행 중인 구간은 상위 봉 rollup에 불안정한 값을 넣을 수 있으므로 저장하지 않는다. 외부 API가 provider timestamp를 제공하면 provider timestamp가 이 직전 완료 구간 안에 있는지 검증하고, 맞지 않으면 해당 종목 결과를 failed로 기록한다.

## 정규화

외부 API는 신뢰하지 않으며 `unknown`에서 보증합니다. 필수 값은 다음이다.

```txt
open
high
low
close
volume
provider timestamp or request timestamp
```

실패할 시 가격표를 기록하지 않고 `ingestion_symbol_results.status = failed`로 기록합니다.

## Upsert

`stock_price_bars` upsert 키:

```txt
source, market_code, symbol, timeframe, interval_start, session_type
```

같은 간격을 다시 수집해도 행을 의심할 여지가 없습니다.

## 실패 처리

종류:

- API 200 + 유효한 OHLCV: `success`
- API 429: `failed`, `api_status = 429`
- API 5xx: `failed`
- 시간 초과: `failed`
- 유효하지 않은 페이로드: `failed`

실행 단위:

- 시도한 모든 기호 성공: `success`
- 일부 성공, 일부 실패: `partial_success`
- 시도된 기호는 모두 실패: `failed`
- 시장이 늦는다: `skipped_market_closed`

Queue는 초기 디자이너에 대해 이야기합니다. 스펙트럼의 대기열은 무료 계획 운영 예산을 빠르게 소모할 수 있습니다. 재시도는 다음 Cron 실행과 DB upsert로 처리합니다.

## KV 사용량

KV는 상태를 유지하고 저장한다.

예:

```json
{
  "last_run_at": "2026-05-23T01:00:00Z",
  "last_success_at": "2026-05-23T00:50:00Z",
  "last_status": "partial_success",
  "last_market_code": "us"
}
```

KV는 결국 일관성을 유지하는 구문의 단순화된 트랜잭션 내용에 사용되지 않습니다. 최종 기준은 Supabase Unique Key와 upsert다.
