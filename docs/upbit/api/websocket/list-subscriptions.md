# WebSocket - 구독 중인 스트림 목록 조회

출처: https://docs.upbit.com/kr/reference/list-subscriptions  
정리일: 2026-05-29

## 핵심 요약

현재 WebSocket 연결에서 구독 중인 데이터 스트림 목록을 조회한다. 일반 데이터 구독 요청과 달리 `type`이 아니라 `method` 필드를 사용하는 Operation 메시지다.

## Request Method Object

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `method` | String | 필수 | `LIST_SUBSCRIPTIONS` |

## 요청 예시

```json
[
  {"ticket": "unique-ticket"},
  {"method": "LIST_SUBSCRIPTIONS"}
]
```

## Format 주의사항

구독 목록 조회 요청에 `format` 필드를 지정하면 기존 구독 스트림의 응답 형식도 변경될 수 있다.

예를 들어 기존에 `SIMPLE` 형식으로 실시간 스트림을 수신 중인데, 구독 목록 조회를 `DEFAULT` 형식으로 요청하면 기존 스트림도 `DEFAULT` 형식으로 수신될 수 있다. 기존 구독 형식과 동일한 `format`을 사용하거나, 불필요하면 `format` 지정을 피한다.

## 요청 수 제한

구독 목록 조회 요청도 WebSocket 요청 수 제한 대상이다.

관련 제한:

- `websocket-message`: 초당 최대 5회, 분당 100회

## 응답 필드

| 필드 | 축약형 | 설명 |
| --- | --- | --- |
| `method` | `mthd` | 요청 메서드. `LIST_SUBSCRIPTIONS` |
| `result` | `rslt` | 구독 중인 스트림 목록 |
| `result.type` | `rslt.ty` | 데이터 타입 |
| `result.codes` | `rslt.cds` | 페어 코드 목록 |
| `result.level` | `rslt.lv` | 호가 모아보기 단위 |
| `ticket` | `tckt` | 요청자 식별 값 |

## 응답 예시

Quotation 스트림:

```json
{
  "method": "LIST_SUBSCRIPTIONS",
  "result": [
    {"type": "ticker", "codes": ["KRW-BTC", "KRW-ETH"]},
    {"type": "orderbook", "codes": ["KRW-BTC", "KRW-ETH"], "level": 0}
  ],
  "ticket": "unique-ticket"
}
```

Exchange 스트림:

```json
{
  "method": "LIST_SUBSCRIPTIONS",
  "result": [
    {"type": "myAsset"},
    {"type": "myOrder", "codes": ["KRW-BTC", "KRW-ETH"]}
  ],
  "ticket": "unique-ticket"
}
```

## 구현 체크리스트

- 현재 연결의 구독 상태 점검용으로 사용한다.
- 요청 자체도 WebSocket message 제한을 소모한다.
- 기존 스트림 포맷이 바뀌지 않도록 `format` 지정에 주의한다.
- 재구독 로직 검증이나 연결 복구 이후 상태 점검에 활용할 수 있다.
