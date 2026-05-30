# WebSocket - 현재가(Ticker)

출처: https://docs.upbit.com/kr/reference/websocket-ticker  
정리일: 2026-05-29

## 핵심 요약

현재가 데이터를 WebSocket으로 구독한다. Quotation 데이터이므로 공개 WebSocket Endpoint를 사용하며 인증은 필요 없다.

```text
wss://api.upbit.com/websocket/v1
```

## Request Data Type Object

| 필드 | 타입 | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- | --- |
| `type` | String | 필수 | 없음 | `ticker` |
| `codes` | List:String | 필수 | 없음 | 수신할 페어 목록. 반드시 대문자 |
| `is_only_snapshot` | Boolean | 선택 | `false` | 스냅샷만 수신 |
| `is_only_realtime` | Boolean | 선택 | `false` | 실시간 데이터만 수신 |

## 요청 예시

```json
[
  {"ticket": "unique-ticket"},
  {"type": "ticker", "codes": ["KRW-BTC", "KRW-ETH"]},
  {"format": "DEFAULT"}
]
```

SIMPLE_LIST 포맷:

```json
[
  {"ticket": "unique-ticket"},
  {"type": "ticker", "codes": ["KRW-BTC", "KRW-ETH"]},
  {"format": "SIMPLE_LIST"}
]
```

## 주요 응답 필드

| 필드 | 축약형 | 설명 |
| --- | --- | --- |
| `type` | `ty` | 데이터 항목. `ticker` |
| `code` | `cd` | 페어 코드 |
| `opening_price` | `op` | 시가 |
| `high_price` | `hp` | 고가 |
| `low_price` | `lp` | 저가 |
| `trade_price` | `tp` | 현재가 |
| `prev_closing_price` | `pcp` | 전일 종가 |
| `change` | `c` | 전일 종가 대비 방향. `RISE`, `EVEN`, `FALL` |
| `change_price` | `cp` | 전일 대비 가격 변동 절대값 |
| `signed_change_price` | `scp` | 전일 대비 가격 변동 값 |
| `change_rate` | `cr` | 전일 대비 등락률 절대값 |
| `signed_change_rate` | `scr` | 전일 대비 등락률 |
| `trade_volume` | `tv` | 최근 거래량 |
| `acc_trade_volume` | `atv` | 누적 거래량. UTC 0시 기준 |
| `acc_trade_volume_24h` | `atv24h` | 최근 24시간 누적 거래량 |
| `acc_trade_price` | `atp` | 누적 거래대금. UTC 0시 기준 |
| `acc_trade_price_24h` | `atp24h` | 최근 24시간 누적 거래대금 |
| `trade_timestamp` | `ttms` | 체결 타임스탬프(ms) |
| `ask_bid` | `ab` | 최근 체결의 매수/매도 구분. `ASK`, `BID` |
| `market_state` | `ms` | 거래 상태. `PREVIEW`, `ACTIVE`, `DELISTED` |
| `delisting_date` | `dd` | 거래지원 종료일 |
| `timestamp` | `tms` | 이벤트 타임스탬프(ms) |
| `stream_type` | `st` | `SNAPSHOT` 또는 `REALTIME` |

## Deprecated 필드

- `is_trading_suspended`
- `market_warning`

신규 구현에서는 참조 대상에서 제외하는 것이 좋다.

## 구현 체크리스트

- 페어 코드는 대문자로 요청한다.
- 최초 스냅샷과 실시간 이벤트를 구분하려면 `stream_type`을 확인한다.
- 대량 페어 구독 시 `SIMPLE` 또는 `SIMPLE_LIST`로 트래픽을 줄일 수 있다.
- 시장 상태 판단에는 deprecated 필드보다 `market_state`, `delisting_date`를 우선 사용한다.
