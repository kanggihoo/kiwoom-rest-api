# WebSocket - 호가(Orderbook)

출처: https://docs.upbit.com/kr/reference/websocket-orderbook  
정리일: 2026-05-29

## 핵심 요약

페어별 호가 데이터를 WebSocket으로 구독한다. Quotation 데이터이므로 공개 WebSocket Endpoint를 사용하며 인증은 필요 없다.

```text
wss://api.upbit.com/websocket/v1
```

## 호가 모아보기(level)

- `level`은 원화마켓(KRW)에서만 지원한다.
- 숫자 형식의 값으로 요청한다.
- 예: `level=100000`이면 `KRW-BTC` 호가를 10만원 단위로 묶어 ask/bid price와 size를 반환한다.
- 지원하지 않는 모아보기 단위를 요청하면 데이터가 수신되지 않을 수 있다.
- 지원 단위는 [호가 정책 조회](../quotation/orderbooks.md) 또는 마켓별 주문 정책을 참고한다.

## 호가 조회 개수(unit)

`codes` 값에 `{pair_code}.{unit}` 형식으로 조회할 호가 쌍 개수를 지정할 수 있다.

```text
KRW-BTC.15
```

지원 단위:

```text
1, 5, 15, 30
```

별도 지정이 없으면 기본적으로 30개 호가 쌍이 반환된다.

## Request Data Type Object

| 필드 | 타입 | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- | --- |
| `type` | String | 필수 | 없음 | `orderbook` |
| `codes` | List:String | 필수 | 없음 | 수신할 페어 목록. 반드시 대문자. `{pair_code}.{unit}` 형식 가능 |
| `level` | Double | 선택 | `0` | 호가 모아보기 단위 |
| `is_only_snapshot` | Boolean | 선택 | `false` | 스냅샷만 수신 |
| `is_only_realtime` | Boolean | 선택 | `false` | 실시간 데이터만 수신 |

## 요청 예시

```json
[
  {"ticket": "unique-ticket"},
  {"type": "orderbook", "codes": ["KRW-BTC", "KRW-ETH.5"], "level": 10000},
  {"format": "DEFAULT"}
]
```

페어별로 다른 `level`을 적용하려면 data type object를 분리한다.

```json
[
  {"ticket": "unique-ticket"},
  {"type": "orderbook", "codes": ["KRW-BTC"], "level": 10000},
  {"type": "orderbook", "codes": ["KRW-BTT"], "level": 0},
  {"format": "DEFAULT"}
]
```

## 주요 응답 필드

| 필드 | 축약형 | 설명 |
| --- | --- | --- |
| `type` | `ty` | 데이터 항목. `orderbook` |
| `code` | `cd` | 페어 코드 |
| `total_ask_size` | `tas` | 매도 총 잔량 |
| `total_bid_size` | `tbs` | 매수 총 잔량 |
| `orderbook_units` | `obu` | 호가 목록 |
| `orderbook_units.ask_price` | `obu.ap` | 매도 호가 |
| `orderbook_units.bid_price` | `obu.bp` | 매수 호가 |
| `orderbook_units.ask_size` | `obu.as` | 매도 잔량 |
| `orderbook_units.bid_size` | `obu.bs` | 매수 잔량 |
| `timestamp` | `tms` | 타임스탬프(ms) |
| `level` | `lv` | 호가 모아보기 단위 |
| `stream_type` | `st` | `SNAPSHOT` 또는 `REALTIME` |

## 구현 체크리스트

- KRW 외 BTC/USDT 마켓은 `level=0`만 사용한다고 보고 처리한다.
- 미지원 `level` 또는 잘못된 unit 요청 시 데이터가 없을 수 있으므로 구독 전 정책을 확인한다.
- 호가 depth를 줄일 수 있으면 `{pair_code}.1`, `{pair_code}.5`처럼 unit을 명시해 트래픽을 줄인다.
- REST 호가 스냅샷과 병행할 경우 `timestamp` 기준으로 최신성을 비교한다.
