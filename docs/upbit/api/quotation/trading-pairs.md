# Quotation API - 페어 목록 조회

출처: https://docs.upbit.com/kr/reference/list-trading-pairs  
정리일: 2026-05-29

## 핵심 요약

업비트에서 거래 가능한 페어 목록을 조회한다. Quotation API이므로 인증 없이 호출할 수 있다.

## Endpoint

```http
GET https://api.upbit.com/v1/market/all
```

## Rate Limit

| 항목 | 내용 |
| --- | --- |
| 그룹 | `market` |
| 제한 | 초당 최대 10회 |
| 측정 단위 | IP 단위 |
| 공유 범위 | 마켓 그룹 내 API와 요청 가능 횟수 공유 |

## Query Parameters

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `is_details` | boolean | 선택 | 상세 정보 포함 여부. `true` 지정 시 페어별 시장경보 등 상세 필드 조회 |

## 응답 개념

응답은 거래 가능한 페어 목록이다. 일반적으로 다음 성격의 정보를 사용한다.

- 페어 코드: 예 `KRW-BTC`
- 한글/영문 페어명
- 시장 경보 또는 상세 상태 정보
- 이벤트성 마켓 정보

## 변경 이력 메모

- 2024-11-20: `market_event` 필드 신규 지원, `market_warning` 필수 여부 변경
- 2024-02-22: 페어별 시장경보 조회 지원
- 이전: `is_details` 파라미터 지원

## 구현 체크리스트

- 앱 시작 시 또는 주기적 캐시 갱신 용도로 사용한다.
- 주문/시세 API 호출 전 유효한 페어인지 검증하는 기준 데이터로 활용한다.
- `is_details=true`를 사용할 경우 경보/이벤트 필드를 파싱할 수 있게 모델을 열어 둔다.
- 모든 Quotation API처럼 인증 헤더는 필요 없다.
