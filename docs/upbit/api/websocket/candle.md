# WebSocket - 캔들(Candle)

출처: https://docs.upbit.com/kr/reference/websocket-candle  
정리일: 2026-05-29

## 핵심 요약

캔들 데이터를 WebSocket으로 구독한다. Quotation 데이터이므로 공개 WebSocket Endpoint를 사용하며 인증은 필요 없다.

```text
wss://api.upbit.com/websocket/v1
```

## 전송 방식

- 실시간 스트림 전송 주기는 1초다.
- 캔들은 해당 시간대에 체결이 발생해 직전 캔들 대비 데이터가 변경될 때만 생성된다.
- 1초가 지나도 체결이 없으면 실시간 캔들 데이터가 전송되지 않을 수 있다.
- 요청 시점에 해당 단위의 현재 캔들이 아직 생성되지 않았으면 이전 시간 단위의 데이터가 최초 스냅샷으로 전송될 수 있다.
- 같은 `candle_date_time` 데이터가 여러 번 전송될 수 있으며, 가장 마지막으로 수신한 데이터가 최신이다.

## 지원 type

| type | 설명 |
| --- | --- |
| `candle.1s` | 초봉 |
| `candle.1m` | 1분봉 |
| `candle.3m` | 3분봉 |
| `candle.5m` | 5분봉 |
| `candle.10m` | 10분봉 |
| `candle.15m` | 15분봉 |
| `candle.30m` | 30분봉 |
| `candle.60m` | 60분봉 |
| `candle.240m` | 240분봉 |

## Request Data Type Object

| 필드 | 타입 | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- | --- |
| `type` | String | 필수 | 없음 | `candle.1s`, `candle.1m` 등 캔들 타입 |
| `codes` | List | 필수 | 없음 | 수신할 페어 목록. 반드시 대문자 |
| `is_only_snapshot` | Boolean | 선택 | `false` | 스냅샷만 수신 |
| `is_only_realtime` | Boolean | 선택 | `false` | 실시간 데이터만 수신 |

## 요청 예시

```json
[
  {"ticket": "unique-ticket"},
  {"type": "candle.1s", "codes": ["KRW-BTC", "KRW-ETH"]},
  {"format": "DEFAULT"}
]
```

## 주요 응답 필드

| 필드 | 축약형 | 설명 |
| --- | --- | --- |
| `type` | `ty` | 캔들 타입 |
| `code` | `cd` | 페어 코드 |
| `candle_date_time_utc` | `cdttmu` | 캔들 기준 시각. UTC |
| `candle_date_time_kst` | `cdttmk` | 캔들 기준 시각. KST |
| `opening_price` | `op` | 시가 |
| `high_price` | `hp` | 고가 |
| `low_price` | `lp` | 저가 |
| `trade_price` | `tp` | 종가 |
| `candle_acc_trade_volume` | `catv` | 누적 거래량 |
| `candle_acc_trade_price` | `catp` | 누적 거래 금액 |
| `timestamp` | `tms` | 타임스탬프(ms) |
| `stream_type` | `st` | `SNAPSHOT` 또는 `REALTIME` |

## 구현 체크리스트

- 캔들 키는 `code + type + candle_date_time_utc` 조합으로 관리한다.
- 같은 캔들 시간이 여러 번 올 수 있으므로 마지막 수신 값을 upsert한다.
- 체결 없는 구간에는 이벤트가 없을 수 있으므로 1초마다 새 캔들이 온다고 가정하지 않는다.
- 빈 구간 보정이나 과거 데이터 로딩은 REST [candles.md](../quotation/candles.md)를 함께 사용한다.
