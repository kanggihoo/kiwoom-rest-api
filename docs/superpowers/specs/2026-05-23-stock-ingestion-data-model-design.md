# 주식 수집 데이터 모델 설계

작성일: 2026-05-23

## 목적

주식 OHLCV 고정 데이터, 수집 대상, 수집 실행 결과, 정리 작업 결과를 분리해 저장합니다. 가격 데이터는 단일 테이블에 저장하고 `timeframe`으로 10분봉, 30분봉, 1시간봉, 일봉을 구분한다.

##관계

```txt
markets
  1 -- N watchlist_symbols
  1 -- N stock_price_bars
  1 -- N ingestion_runs

watchlist_symbols
  1 -- N stock_price_bars

ingestion_runs
  1 -- N ingestion_symbol_results

pg_cron
  stock_price_bars(timeframe='10m')
    -> stock_price_bars(timeframe='30m')
    -> stock_price_bars(timeframe='1h')
    -> stock_price_bars(timeframe='1d')
```

## 시장

시장을 정의하는 테이블이다.

| 칼럼 | 의미 |
| --- | --- |
| '코드' | 시장 코드. 예: `krx`, `us`. 다른 테이블의 시장 기준 값이다. |
| `시간대` | 시장 구분. 예: `아시아/서울`, `미국/뉴욕`. 구성요소와 거래일을 처리하는 데 사용됩니다. |
| `정기_오픈` | 교육장 시작 시간. 시장 현지 시간 기준이다. |
| `regular_close` | 정규 종료 시간. 시장 현지 시간 기준이다. |
| '활성화' | 이 시장의 수집 활성화 여부. |

## watchlist_symbols

수집 대상과 우선 순위를 관리합니다.

| 칼럼 | 의미 |
| --- | --- |
| `기호` | 내부 코드. 예: `AAPL`, `005930`. |
| `시장_코드` | 소속 시장. `markets.code`를 참조하세요. |
| '우선순위' | 수집 우선 순위. 미를 점점 더 먼저한다. |
| '활성화' | 이의 수집 활성화 여부. |
| `소스_기호` | 외부 주식 API는 기호 형식을 요구합니다. 내부 기호와 사용할 수 있습니다. |
| `마지막_성공_at` | 이 소파의 마지막 성공 수집기입니다. |
| `마지막_오류_at` | 이 장인은 실패할 것입니다. |

## 재고_가격_바

가격 변동 데이터 테이블입니다. Worker는 `10m`만 직접 저장하고, pg_cron이 `30m`, `1h`, `1d`를 생성합니다.

| 칼럼 | 의미 |
| --- | --- |
| '출처' | 데이터 제공자 이름. API 교체 또는 복수 공급자 비교에 사용합니다. |
| `시장_코드` | 시장 코드. |
| `기호` | 코드. |
| `기간` | 고유의. 초기값은 `10m`, `30m`, `1h`, `1d`다입니다. |
| '간격_시작' | 해당 봉의 시작하겠습니다. 시간대가 포함된 타임스탬프를 사용합니다. |
| `세션_유형` | 거래 세션. 처음에는 `정기`만 사용하고, 나중에 `pre_market`, `after_hours`를 추가할 수 있습니다. |
| '오픈' | 해당 봉의 시작 가격. |
| '높음' | 해당 봉의 최고 가격. |
| '낮음' | 해당 봉의 가격. |
| '닫기' | 해당 봉의 종가. |
| '볼륨' | 해당하는 금액의 거래량입니다. |
| `공급자_시간` | 외부 API가 준 원본 타임스탬프입니다. 수집기에서는 주로 사용하고 있으며 null일 수 있습니다. |
| `소스_행_개수` | 이 봉을 만들 때 용도 하위 봉 행을 사용할 수 있습니다. 10분봉 원본은 1이다. |
| `created_at` | DB 처음 저장했어요. |
| 'updated_at' | 마지막으로요. |

복합적인 주제:

```txt
unique(source, market_code, symbol, timeframe, interval_start, session_type)
```

주요지수:

```txt
unique(source, market_code, symbol, timeframe, interval_start, session_type)
index(market_code, symbol, timeframe, interval_start desc)
index(timeframe, interval_start)
```

## ingestion_runs

Cloudflare Cron Worker 실행 반대 결과.

| 칼럼 | 의미 |
| --- | --- |
| `run_id` | Cron 실행을 실행합니다. |
| `예정_기간` | 원래 수집한 거야. 실제로 실행해 볼 수 있습니다. |
| `시장_코드` | 이번 run이 대상으로 삼은 시장. |
| `상태` | `성공`, `부분 성공`, `실패`, `skipped_market_closed` 등. |
| `시작된_시간` | 진짜 시작이군요. |
| `finished_at` | 진짜 종료됐어. |
| `하위 요청_예산` | 법인 API 호출에 가정한 최대 호출 수 있습니다. |
| `기호_계획` | 대신해 줄 수 있습니다. |
| `기호_시도` | 실제로 API를 호출할 수 있습니다. |
| `기호_성공` | 이럴 수 있습니다. |
| `symbols_failed` | 통화할 수 있습니다. |
| `오류_메시지` | 전체 대표를 실행하세요. |

## ingestion_symbol_results

한 Cron 실행으로 인해 별 결과를 저장합니다.

| 칼럼 | 의미 |
| --- | --- |
| `run_id` | `ingestion_runs.run_id`를 참조합니다. |
| `기호` | 코드. |
| `시장_코드` | 시장 코드. |
| `상태` | `성공`, `실패`, `건너뛴_예산` 등. |
| `api_status` | 외부 API HTTP 상태 또는 공급자 상태. |
| '간격_시작' | 저장하면 봉이 시작될 거예요. |
| `오류_메시지` | 단지 이유가 있습니다. |

## 유지 관리_실행

pg_cron 기반 롤업/삭제 작업 결과.

| 칼럼 | 의미 |
| --- | --- |
| `직업_이름` | 이름. 예: `rollup_10m_to_1d`, `delete_old_bars`. |
| `시장_코드` | 대상시장. |
| `시작된_시간` | 작업을 시작하겠습니다. |
| `finished_at` | 작업이 종료되었습니다. |
| `상태` | `성공` 또는 `실패`. |
| `rows_rolled_up` | 생성하거나 상위 행을 만들 수 있습니다. |
| `행_삭제됨` | 하위 기간 행을 삭제할 수 있습니다. |
| `오류_메시지` | 실패 이유. |

## 건강 뷰

Grafana와 SQL 확인을 위해 view를 죽입니다.

```txt
v_ingestion_health
v_symbol_health
v_maintenance_health
```

`v_ingestion_health`는 시장별 마지막 성공, 실패, 부분적 성공을 나타냅니다. `v_symbol_health`는 별 마지막 성공/실패와 24시간 실패하는 것을 보여줍니다. `v_maintenance_health`는 롤업/삭제 작업의 최근 성공 여부와 처리 행을 표시합니다.
