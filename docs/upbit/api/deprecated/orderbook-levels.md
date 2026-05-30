# Deprecated - 호가 모아보기 단위 조회

출처: https://docs.upbit.com/kr/reference/list-orderbook-levels  
정리일: 2026-05-29

## 상태

이 API는 Deprecated 상태다. 신규 구현에서는 [호가 정책 조회](../quotation/orderbooks.md)를 우선 사용한다.

## 핵심 요약

종목별로 지원하는 호가 모아보기 단위 목록을 조회한다. 반환된 단위는 호가 조회 API의 `level` 값으로 사용할 수 있다.

호가 모아보기 기능은 현재 원화마켓(KRW)만 지원한다. 지원 대상이 아닌 페어는 기본값 `0`만 지원 단위로 반환된다.

## Endpoint

```http
GET https://api.upbit.com/v1/orderbook/supported_levels
```

## Rate Limit

| 항목 | 내용 |
| --- | --- |
| 그룹 | `orderbook` |
| 제한 | 초당 최대 10회 |
| 측정 단위 | IP 단위 |
| 공유 범위 | 호가 그룹 내 API와 요청 가능 횟수 공유 |

## Query Parameters

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `markets` | string | 필수 | 조회할 페어 목록. 2개 이상은 쉼표로 구분 |

예:

```text
KRW-BTC,KRW-ETH,BTC-ETH,BTC-XRP
```

## 응답 필드

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `market` | string | 페어 코드 |
| `supported_levels` | number[] | 해당 페어에서 지원하는 호가 모아보기 단위 |

`supported_levels`에서 `0`은 기본 호가 단위를 의미한다. BTC, USDT 마켓처럼 호가 모아보기를 지원하지 않는 경우 일반적으로 `0`만 존재한다.

## 응답 예시

```json
[
  {
    "market": "KRW-BTC",
    "supported_levels": [0, 10000, 100000, 1000000, 10000000, 100000000]
  },
  {
    "market": "KRW-ETH",
    "supported_levels": [0, 10000, 100000, 1000000]
  },
  {
    "market": "KRW-TRX",
    "supported_levels": [0, 1, 10, 100]
  },
  {
    "market": "KRW-XRP",
    "supported_levels": [0, 10, 100, 1000]
  }
]
```

## 에러

| HTTP 상태 | 의미 |
| --- | --- |
| 400 | 파라미터 타입 오류 또는 필수 파라미터 누락 |
| 404 | 요청한 페어 코드를 찾을 수 없음 |

## 변경 이력 메모

- v1.4.4, 2024-01-22: 원화 마켓 호가 모아보기 기능 신규 지원

## 구현 체크리스트

- 신규 구현에서는 이 Deprecated API 대신 호가 정책 조회 API를 사용한다.
- 기존 코드 유지보수 시 `markets`는 쉼표 구분 문자열로 구성한다.
- `supported_levels`에 없는 값을 호가 조회 `level`로 요청하지 않는다.
- KRW 마켓 외에는 `0`만 반환될 수 있으므로 모아보기 UI를 비활성화한다.
- 이 API도 `orderbook` 그룹 Rate Limit을 사용하므로 호가 조회 API와 제한을 공유한다.
