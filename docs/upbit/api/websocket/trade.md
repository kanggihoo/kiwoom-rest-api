# WebSocket - 체결(Trade)

출처: https://docs.upbit.com/kr/reference/websocket-trade  
정리일: 2026-05-29

## 핵심 요약

페어별 체결 데이터를 WebSocket으로 구독한다. Quotation 데이터이므로 공개 WebSocket Endpoint를 사용하며 인증은 필요 없다.

```text
wss://api.upbit.com/websocket/v1
```

## Request Data Type Object

| 필드 | 타입 | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- | --- |
| `type` | String | 필수 | 없음 | `trade` |
| `codes` | List:String | 필수 | 없음 | 수신할 페어 목록. 반드시 대문자 |
| `is_only_snapshot` | Boolean | 선택 | `false` | 스냅샷만 수신 |
| `is_only_realtime` | Boolean | 선택 | `false` | 실시간 데이터만 수신 |

## 요청 예시

```json
[
  {"ticket": "unique-ticket"},
  {"type": "trade", "codes": ["KRW-BTC", "KRW-ETH"]},
  {"format": "DEFAULT"}
]
```

## 주요 응답 필드

| 필드 | 축약형 | 설명 |
| --- | --- | --- |
| `type` | `ty` | 데이터 항목. `trade` |
| `code` | `cd` | 페어 코드 |
| `trade_price` | `tp` | 체결 가격 |
| `trade_volume` | `tv` | 체결량 |
| `ask_bid` | `ab` | 매수/매도 구분. `ASK`, `BID` |
| `prev_closing_price` | `pcp` | 전일 종가 |
| `change` | `c` | 전일 종가 대비 방향. `RISE`, `EVEN`, `FALL` |
| `change_price` | `cp` | 전일 대비 가격 변동 절대값 |
| `trade_date` | `td` | 체결 일자. UTC, `yyyy-MM-dd` |
| `trade_time` | `ttm` | 체결 시각. UTC, `HH:mm:ss` |
| `trade_timestamp` | `ttms` | 체결 타임스탬프(ms) |
| `timestamp` | `tms` | 이벤트 타임스탬프(ms) |
| `sequential_id` | `sid` | 체결 번호 |
| `best_ask_price` | `bap` | 최우선 매도 호가 |
| `best_ask_size` | `bas` | 최우선 매도 잔량 |
| `best_bid_price` | `bbp` | 최우선 매수 호가 |
| `best_bid_size` | `bbs` | 최우선 매수 잔량 |
| `stream_type` | `st` | `SNAPSHOT` 또는 `REALTIME` |

## 구현 체크리스트

- 체결 기반 전략은 `trade_timestamp` 또는 `sequential_id`로 중복/순서를 관리한다.
- 최초 스냅샷과 실시간 체결을 구분하려면 `stream_type`을 확인한다.
- 호가 최우선 가격/잔량이 함께 내려오므로 체결 시점의 top-of-book 참고값으로 사용할 수 있다.
- 과거 체결 보정은 REST [trades.md](../quotation/trades.md)를 함께 사용한다.
