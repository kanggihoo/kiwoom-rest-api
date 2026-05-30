# WebSocket API 인덱스

정리일: 2026-05-29  
대상: 업비트 WebSocket API

## Endpoint

| 구분 | Endpoint | 인증 |
| --- | --- | --- |
| Quotation | `wss://api.upbit.com/websocket/v1` | 불필요 |
| Exchange | `wss://api.upbit.com/websocket/v1/private` | JWT 인증 필요 |

## 문서 목록

| 파일 | 원문 | 내용 |
| --- | --- | --- |
| [ticker.md](./ticker.md) | [현재가(Ticker)](https://docs.upbit.com/kr/reference/websocket-ticker) | 현재가 스트림, 가격 변동 지표, 거래 상태 필드 |
| [trade.md](./trade.md) | [체결(Trade)](https://docs.upbit.com/kr/reference/websocket-trade) | 체결 스트림, 체결 가격/량, 최우선 호가, 체결 식별자 |
| [orderbook.md](./orderbook.md) | [호가(Orderbook)](https://docs.upbit.com/kr/reference/websocket-orderbook) | 호가 스트림, `level`, `{pair_code}.{unit}`, 호가 배열 |
| [candle.md](./candle.md) | [캔들(Candle)](https://docs.upbit.com/kr/reference/websocket-candle) | 초/분 캔들 스트림, 중복 캔들 시간 처리, OHLCV 필드 |
| [myorder.md](./myorder.md) | [내 주문 및 체결(MyOrder)](https://docs.upbit.com/kr/reference/websocket-myorder) | Private 주문/체결 이벤트, 주문 상태, SMP 필드 |
| [myasset.md](./myasset.md) | [내 자산(MyAsset)](https://docs.upbit.com/kr/reference/websocket-myasset) | Private 자산 변동 이벤트, 자산 목록, 최초 구독 주의사항 |
| [list-subscriptions.md](./list-subscriptions.md) | [구독 중인 스트림 목록 조회](https://docs.upbit.com/kr/reference/list-subscriptions) | `LIST_SUBSCRIPTIONS` operation 메시지, 응답 구조, format 주의사항 |

## Request Object 빠른 표

| 타입 | Endpoint | 인증 | 필수 필드 | 선택 필드 |
| --- | --- | --- | --- | --- |
| `ticker` | Quotation | 없음 | `type`, `codes` | `is_only_snapshot`, `is_only_realtime` |
| `trade` | Quotation | 없음 | `type`, `codes` | `is_only_snapshot`, `is_only_realtime` |
| `orderbook` | Quotation | 없음 | `type`, `codes` | `level`, `is_only_snapshot`, `is_only_realtime` |
| `candle.{unit}` | Quotation | 없음 | `type`, `codes` | `is_only_snapshot`, `is_only_realtime` |
| `myOrder` | Exchange | 필요 | `type` | `codes` |
| `myAsset` | Exchange | 필요 | `type` | 없음 |
| `LIST_SUBSCRIPTIONS` | 현재 연결 | 연결별 | `method` | `format` |

## 공통 메시지 구조

일반 데이터 구독:

```json
[
  {"ticket": "unique-ticket"},
  {"type": "ticker", "codes": ["KRW-BTC"]},
  {"format": "DEFAULT"}
]
```

구독 목록 조회:

```json
[
  {"ticket": "unique-ticket"},
  {"method": "LIST_SUBSCRIPTIONS"}
]
```

## Format

| format | 설명 |
| --- | --- |
| `DEFAULT` | 기본 응답 필드명 |
| `SIMPLE` | 축약 필드명 |
| `JSON_LIST` | 리스트 포맷 |
| `SIMPLE_LIST` | 축약 필드명의 리스트 포맷 |

## 요청 수 제한

| 그룹 | 제한 |
| --- | --- |
| `websocket-connect` | 초당 최대 5회 |
| `websocket-message` | 초당 최대 5회, 분당 100회 |

`Origin` 헤더가 포함된 요청은 별도 제한이 적용될 수 있다. 자세한 내용은 [rate-limits.md](../rate-limits.md)를 참고한다.

## 구현 메모

- Quotation 타입은 인증 없이 사용한다.
- `myOrder`, `myAsset`은 JWT 인증이 필요하며 Private Endpoint로 연결한다.
- `codes`가 필요한 타입은 페어 코드를 대문자로 보낸다.
- `myAsset`은 `codes`를 지원하지 않는다.
- 이벤트가 없을 때 데이터가 오지 않는 타입이 있으므로 연결 유지와 이벤트 수신 여부를 분리해 판단한다.
- 구독 상태 점검에는 `LIST_SUBSCRIPTIONS`를 사용하되, 기존 스트림 format 변경에 주의한다.
