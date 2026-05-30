# Quotation API - 현재가 조회

출처:

- https://docs.upbit.com/kr/reference/list-tickers
- https://docs.upbit.com/kr/reference/list-quote-tickers

정리일: 2026-05-29

## 핵심 요약

현재가 API는 페어 단위 또는 마켓 단위로 최근 가격, 전일 대비 변동, 거래량 등 현재 시세 정보를 조회한다.

## 공통 Rate Limit

| 항목 | 내용 |
| --- | --- |
| 그룹 | `ticker` |
| 제한 | 초당 최대 10회 |
| 측정 단위 | IP 단위 |
| 공유 범위 | 현재가 그룹 내 요청 가능 횟수 공유 |

## 페어 단위 현재가 조회

```http
GET https://api.upbit.com/v1/ticker
```

### Query Parameters

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `markets` | string | 필수 | 쉼표로 구분한 페어 코드 목록. 예: `KRW-BTC,KRW-ETH` |

### 사용처

- 관심 페어 목록의 현재가를 한 번에 조회
- 주문 전 현재 시세 확인
- 주기적 가격 갱신

## 마켓 단위 현재가 조회

```http
GET https://api.upbit.com/v1/ticker/all
```

### Query Parameters

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `quote_currencies` | string | 필수 | 조회할 기준 마켓. 예: `KRW`, `BTC`, `USDT` 등 |

### 사용처

- 특정 기준 마켓 전체 페어 현재가를 한 번에 조회
- 전체 시세판, 마켓별 랭킹, 필터링 데이터 구성

## 가격 변동 지표

현재가 응답의 가격 변동 관련 필드는 전일 종가 기준으로 산출된다.

대표 필드:

- `change`
- `change_price`
- `change_rate`
- `signed_change_price`
- `signed_change_rate`

## 변경 이력 메모

- 페어 단위 현재가 조회: 2018-06-21 API 신규 지원
- 마켓 단위 현재가 조회: 2024-09-04 신규 지원

## 구현 체크리스트

- `markets`, `quote_currencies`는 쉼표 구분 문자열 형식으로 구성한다.
- 많은 페어를 자주 갱신해야 하면 WebSocket `ticker` 구독이 더 적합할 수 있다.
- 전일 대비 지표는 전일 종가 기준이므로 사용자가 기대하는 기준 시간과 일치하는지 확인한다.
- 페어 단위와 마켓 단위 API가 같은 `ticker` 그룹 제한을 공유한다.
