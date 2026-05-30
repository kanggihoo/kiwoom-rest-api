# Quotation API - 캔들 조회

출처:

- https://docs.upbit.com/kr/reference/list-candles-seconds
- https://docs.upbit.com/kr/reference/list-candles-minutes
- https://docs.upbit.com/kr/reference/list-candles-days
- https://docs.upbit.com/kr/reference/list-candles-weeks
- https://docs.upbit.com/kr/reference/list-candles-months
- https://docs.upbit.com/kr/reference/list-candles-years

정리일: 2026-05-29

## 핵심 요약

페어별 OHLCV 캔들 데이터를 시간 단위별로 조회한다. 캔들은 해당 시간 구간에 체결이 발생한 경우에만 생성되므로, 체결이 없는 구간은 응답에 포함되지 않을 수 있다.

## 공통 Rate Limit

| 항목 | 내용 |
| --- | --- |
| 그룹 | `candle` |
| 제한 | 초당 최대 10회 |
| 측정 단위 | IP 단위 |
| 공유 범위 | 초/분/일/주/월/년 캔들 API가 같은 캔들 그룹 제한을 공유 |

## 공통 Query Parameters

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `market` | string | 필수 | 조회할 페어 코드. 예: `KRW-BTC` |
| `to` | string | 선택 | 조회 기준 시각 |
| `count` | integer | 선택 | 조회 개수. 기본값 `1` |

## Endpoint 목록

| 단위 | Endpoint | 추가 조건 |
| --- | --- | --- |
| 초 | `GET /v1/candles/seconds` | 최근 3개월 이내 데이터만 제공 |
| 분 | `GET /v1/candles/minutes/{unit}` | `unit` 필수 |
| 일 | `GET /v1/candles/days` | `converting_price_unit` 선택 |
| 주 | `GET /v1/candles/weeks` | 공통 파라미터 사용 |
| 월 | `GET /v1/candles/months` | 공통 파라미터 사용 |
| 연 | `GET /v1/candles/years` | 공통 파라미터 사용 |

Base URL:

```text
https://api.upbit.com
```

## 초 캔들

```http
GET https://api.upbit.com/v1/candles/seconds
```

- 초 캔들 조회 가능 기간은 요청 시점 기준 최근 3개월이다.
- 조회 가능 기간을 초과하면 빈 리스트가 반환되거나 `count`만큼 반환되지 않을 수 있다.
- `to` 파라미터로 조회 가능 구간을 조정해 확인한다.

## 분 캔들

```http
GET https://api.upbit.com/v1/candles/minutes/{unit}
```

지원 `unit`:

```text
1, 3, 5, 10, 15, 30, 60, 240
```

예를 들어 `/v1/candles/minutes/5`는 체결 정보를 5분 단위로 묶어 캔들을 반환한다.

## 일 캔들

```http
GET https://api.upbit.com/v1/candles/days
```

추가 Query Parameter:

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `converting_price_unit` | string | 선택 | 종가 환산 통화. 현재 원화 `KRW` 환산 지원 |

`converting_price_unit=KRW`를 지정하면 원화 마켓이 아닌 페어의 종가를 원화로 환산한 `converted_trade_price` 필드를 받을 수 있다.

## 주/월/연 캔들

```http
GET https://api.upbit.com/v1/candles/weeks
GET https://api.upbit.com/v1/candles/months
GET https://api.upbit.com/v1/candles/years
```

- 공통 파라미터 `market`, `to`, `count`를 사용한다.
- 연 캔들은 2024-10-30에 신규 지원된 API다.

## 응답 해석 주의사항

- 체결이 없는 시간 구간은 캔들이 생성되지 않는다.
- 따라서 시간 축이 항상 연속된다고 가정하면 안 된다.
- 요청한 `count`보다 적게 반환될 수 있다.
- 백테스트나 차트 생성 시 누락 구간을 클라이언트에서 보정할지 정책을 정해야 한다.

## 구현 체크리스트

- 여러 캔들 단위를 동시에 조회하면 같은 `candle` 그룹 제한을 공유한다.
- 응답 배열 길이가 요청 `count`와 다를 수 있음을 처리한다.
- 초 캔들은 최근 3개월 제한을 반드시 고려한다.
- 분 캔들은 지원 `unit` 외 값 요청 시 오류가 발생할 수 있으므로 enum 검증을 둔다.
- 일 캔들의 원화 환산이 필요할 때만 `converting_price_unit=KRW`를 사용한다.
