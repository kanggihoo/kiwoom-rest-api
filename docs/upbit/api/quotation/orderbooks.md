# Quotation API - 호가 조회

출처:

- https://docs.upbit.com/kr/reference/list-orderbooks
- https://docs.upbit.com/kr/reference/list-orderbook-instruments

정리일: 2026-05-29

## 핵심 요약

호가 API는 페어별 매수/매도 호가와 잔량을 조회한다. 원화 마켓은 `level` 파라미터로 호가를 지정 단위로 묶어 조회할 수 있으며, 지원 단위는 호가 정책 조회 API로 확인한다.

## 공통 Rate Limit

| 항목 | 내용 |
| --- | --- |
| 그룹 | `orderbook` |
| 제한 | 초당 최대 10회 |
| 측정 단위 | IP 단위 |
| 공유 범위 | 호가 그룹 내 요청 가능 횟수 공유 |

## 호가 조회

```http
GET https://api.upbit.com/v1/orderbook
```

### Query Parameters

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- | --- |
| `markets` | string | 필수 | 없음 | 쉼표로 구분한 페어 코드 목록 |
| `level` | string | 선택 | `0` | 호가 모아보기 단위 |
| `count` | integer | 선택 | `30` | 반환할 호가 개수 |

### 호가 모아보기

- `level`은 원화마켓(KRW)에서만 지원한다.
- 숫자 형식의 문자열로 요청한다.
- 예: `level=100000`이면 `KRW-BTC` 호가를 10만원 단위로 묶어 ask/bid price와 size를 반환한다.
- 지원하지 않는 `level`을 요청하면 빈 배열이 반환될 수 있다.
- 페어별 지원 단위는 마켓별 주문 정책 또는 호가 정책 조회 API를 참고한다.

## 호가 정책 조회

```http
GET https://api.upbit.com/v1/orderbook/instruments
```

### Query Parameters

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `markets` | string | 필수 | 쉼표로 구분한 페어 코드 목록 |

### 사용처

- 페어별 지원 호가 단위 확인
- `level` 파라미터 요청 전 유효성 검증
- 호가 모아보기 UI 또는 전략 설정값 구성

## Deprecated API

기존 `GET /v1/orderbook/supported_levels` 호가 모아보기 단위 조회 API는 Deprecated 상태다. 기존 구현 유지보수 정보는 [Deprecated - 호가 모아보기 단위 조회](../deprecated/orderbook-levels.md)를 참고하고, 신규 구현은 호가 정책 조회 API를 사용한다.

## 변경 이력 메모

- 호가 조회
  - 2025-07-02: `count` 파라미터 신규 지원, 최대 30호가 지원
  - 2024-01-22: 원화 마켓 호가 모아보기 기능 신규 지원
- 호가 정책 조회
  - 2025-07-31: 기능 추가

## 구현 체크리스트

- 실시간 호가가 필요하면 WebSocket `orderbook` 구독을 우선 검토한다.
- REST 호가 조회는 초기 스냅샷, 장애 복구, 저빈도 조회에 적합하다.
- `level` 사용 전 호가 정책 조회 API로 지원 단위를 확인한다.
- 미지원 `level` 요청 시 빈 배열이 올 수 있으므로 오류로만 처리하지 않는다.
- `count` 기본값은 30이며, 현재 문서 기준 최대 30호가 지원을 전제로 구현한다.
