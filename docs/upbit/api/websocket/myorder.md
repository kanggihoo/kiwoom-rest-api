# WebSocket - 내 주문 및 체결(MyOrder)

출처: https://docs.upbit.com/kr/reference/websocket-myorder  
정리일: 2026-05-29

## 핵심 요약

내 주문 및 체결 이벤트를 WebSocket으로 구독한다. Exchange 데이터이므로 Private WebSocket Endpoint와 JWT 인증이 필요하다.

```text
wss://api.upbit.com/websocket/v1/private
```

## 전송 방식

- 실제 주문 또는 체결이 발생할 때만 실시간 스트림이 전송된다.
- 연결 후 주문/체결이 없으면 데이터가 수신되지 않는 것이 정상이다.
- 데이터가 없더라도 연결을 유지하려면 WebSocket ping/pong 또는 `"PING"` 메시지 처리를 구현한다.

## Request Data Type Object

| 필드 | 타입 | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- | --- |
| `type` | String | 필수 | 없음 | `myOrder` |
| `codes` | List | 선택 | 전체 마켓 | 수신할 페어 목록. 생략하거나 빈 배열이면 모든 마켓 수신 |

## 요청 예시

모든 페어:

```json
[
  {"ticket": "unique-ticket"},
  {"type": "myOrder"}
]
```

특정 페어:

```json
[
  {"ticket": "unique-ticket"},
  {"type": "myOrder", "codes": ["KRW-BTC"]},
  {"format": "JSON_LIST"}
]
```

## 주요 응답 필드

| 필드 | 축약형 | 설명 |
| --- | --- | --- |
| `type` | `ty` | 데이터 항목. `myOrder` |
| `code` | `cd` | 페어 코드 |
| `uuid` | `uid` | 주문 UUID |
| `ask_bid` | `ab` | 매수/매도 구분. `ASK`, `BID` |
| `order_type` | `ot` | 주문 타입. `limit`, `price`, `market`, `best` |
| `state` | `s` | 주문 상태. `wait`, `watch`, `trade`, `done`, `cancel`, `prevented` |
| `trade_uuid` | `tuid` | 체결 UUID |
| `price` | `p` | 주문 가격 또는 체결 가격 |
| `avg_price` | `ap` | 평균 체결 가격 |
| `volume` | `v` | 주문량 또는 체결량 |
| `remaining_volume` | `rv` | 체결 후 주문 잔량 |
| `executed_volume` | `ev` | 체결된 수량 |
| `trades_count` | `tc` | 해당 주문에 걸린 체결 수 |
| `reserved_fee` | `rsf` | 수수료로 예약된 비용 |
| `remaining_fee` | `rmf` | 남은 수수료 |
| `paid_fee` | `pf` | 사용된 수수료 |
| `locked` | `l` | 거래에 사용 중인 비용 |
| `executed_funds` | `ef` | 체결된 금액 |
| `time_in_force` | `tif` | `ioc`, `fok`, `post_only` |
| `trade_fee` | `tf` | 체결 시 발생한 수수료. `state=trade`가 아니면 null 가능 |
| `is_maker` | `im` | 메이커 여부. `state=trade`가 아니면 null 가능 |
| `identifier` | `id` | 클라이언트 지정 주문 식별자 |
| `smp_type` | `smpt` | 자전거래 체결 방지 타입 |
| `prevented_volume` | `pv` | 체결 방지로 취소된 주문 수량 |
| `prevented_locked` | `pl` | 체결 방지로 취소된 금액 또는 수량 |
| `trade_timestamp` | `ttms` | 체결 타임스탬프(ms) |
| `order_timestamp` | `otms` | 주문 타임스탬프(ms) |
| `timestamp` | `tms` | 이벤트 타임스탬프(ms) |
| `stream_type` | `st` | `REALTIME` 또는 `SNAPSHOT` |

## 변경 이력 메모

2025-07-02 기준 SMP(Self-Match Prevention) 관련 필드와 상태가 추가되었다.

- `smp_type`: `reduce`, `cancel_maker`, `cancel_taker`
- `state=prevented`
- `time_in_force=post_only`

## 구현 체크리스트

- JWT 인증 헤더를 포함해 Private WebSocket에 연결한다.
- 주문 상태 변경은 `uuid`, 체결 이벤트는 `trade_uuid`를 기준으로 중복 처리를 고려한다.
- `state=trade` 이벤트와 최종 `done` 이벤트를 별도로 처리한다.
- `codes` 생략 또는 빈 배열은 전체 마켓 구독이므로 이벤트 양을 고려한다.
- 주문/체결이 없어 이벤트가 오지 않는 상황을 장애로 판단하지 않는다.
