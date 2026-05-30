# 업비트 WebSocket 사용 및 에러 안내

출처: https://docs.upbit.com/kr/reference/websocket-guide  
정리일: 2026-05-29

## Endpoint

| 구분 | Endpoint | 인증 |
| --- | --- | --- |
| Quotation | `wss://api.upbit.com/websocket/v1` | 불필요 |
| Exchange | `wss://api.upbit.com/websocket/v1/private` | 필요 |

## TLS

- TLS 1.2 이상만 지원한다.
- TLS 1.3 사용을 권장한다.

## 인증

Private WebSocket으로 내 주문 또는 내 자산 데이터를 수신하려면 JWT 토큰을 `Authorization` 헤더에 포함해야 한다.

```http
Authorization: Bearer <JWT_TOKEN>
```

일부 WebSocket 클라이언트는 커스텀 헤더 설정을 지원하지 않을 수 있다. Private WebSocket 테스트 전 클라이언트의 헤더 지원 여부를 확인해야 한다.

## 요청 수 제한

WebSocket 요청 수 제한은 [rate-limits.md](./rate-limits.md)를 참고한다.

핵심 제한은 다음과 같다.

| 그룹 | 제한 |
| --- | --- |
| `websocket-connect` | 초당 최대 5회 |
| `websocket-message` | 초당 최대 5회, 분당 100회 |

## 데이터 항목

| type | 구분 | 설명 | 지원 유형 |
| --- | --- | --- | --- |
| `ticker` | Quotation | 현재가 데이터 | 스냅샷, 실시간 스트림 |
| `trade` | Quotation | 체결 데이터 | 스냅샷, 실시간 스트림 |
| `orderbook` | Quotation | 호가 데이터 | 스냅샷, 실시간 스트림 |
| `candle.{unit}` | Quotation | 초봉/분봉 캔들 데이터 | 스냅샷, 실시간 스트림 |
| `myAsset` | Exchange | 내 자산 데이터 | 실시간 스트림 |
| `myOrder` | Exchange | 내 주문 데이터 | 실시간 스트림 |

## 데이터 유형

- 스냅샷: 요청 시점의 정보를 1회 수신한다.
- 실시간 스트림: 연결이 유지되는 동안 이벤트 또는 갱신 주기에 따라 계속 수신한다.
- 별도 지정이 없으면 최초 스냅샷 이후 실시간 데이터가 이어질 수 있다.

## 요청 메시지 구조

WebSocket 데이터 요청 메시지는 JSON Array 형식이다.

### 1. Ticket Object

배열의 첫 번째 요소로 넣는다.

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `ticket` | String | Required | 요청 티켓의 고유 식별자. UUID 등 고유한 문자열 권장 |

### 2. Data Type Object

두 번째 요소부터 구독할 데이터 요청 객체를 넣는다. 여러 객체를 넣어 동시에 여러 데이터를 구독할 수 있다.

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `type` | String | Required | `ticker`, `trade`, `orderbook`, `candle.{unit}`, `myAsset`, `myOrder` 중 하나 |
| `codes` | String[] | Conditional | `ticker`, `trade`, `orderbook`, `candle.{unit}`에서는 필수. `myOrder`에서는 선택 |
| `level` | String | Optional | `orderbook`에서 사용할 호가 모아보기 단위 |
| `is_only_snapshot` | Boolean | Optional | 스냅샷만 요청 |
| `is_only_realtime` | Boolean | Optional | 실시간 스트림만 요청 |

### 3. Format Object

배열의 마지막 요소로 넣을 수 있다.

| format | 설명 |
| --- | --- |
| `DEFAULT` | 기본 포맷 |
| `SIMPLE` | 필드명이 축약어로 반환되는 간략 포맷 |
| `JSON_LIST` | 리스트 포맷 |
| `SIMPLE_LIST` | 축약어 기반 리스트 포맷 |

## 요청 예시

단일 현재가 구독:

```json
[
  {"ticket": "test"},
  {"type": "ticker", "codes": ["KRW-BTC"]}
]
```

체결과 호가를 SIMPLE 포맷으로 구독:

```json
[
  {"ticket": "test"},
  {"type": "trade", "codes": ["KRW-BTC", "BTC-BCH"]},
  {"type": "orderbook", "codes": ["KRW-BTC", "BTC-BCH"]},
  {"format": "SIMPLE"}
]
```

실시간 체결 스트림:

```json
[
  {"ticket": "UNIQUE_TICKET"},
  {"type": "trade", "codes": ["KRW-BTC", "BTC-XRP"]}
]
```

복수 데이터 동시 구독:

```json
[
  {"ticket": "UNIQUE_TICKET"},
  {"type": "trade", "codes": ["KRW-BTC"]},
  {"type": "orderbook", "codes": ["KRW-ETH"]},
  {"type": "ticker", "codes": ["KRW-EOS"]}
]
```

## 연결 관리

- 서버는 120초 동안 데이터 송수신이 없으면 Idle Timeout으로 연결을 종료한다.
- 클라이언트는 주기적으로 PING Frame을 보내 연결을 유지하는 것이 좋다.
- PING Frame 구현이 어렵다면 `"PING"` 메시지를 보낼 수 있다.
- 연결이 정상 유지되면 서버가 10초 간격으로 `{"status":"UP"}` 상태 메시지를 보낼 수 있다.

## 압축

- WebSocket 서버는 압축을 지원한다.
- 클라이언트 라이브러리가 압축 옵션을 지원하면 활성화할 수 있다.
- 일반적으로 압축 해제는 클라이언트/라이브러리가 처리하므로 별도 구현은 필요하지 않다.

## 에러 응답

```json
{
  "error": {
    "name": "ERROR_CODE",
    "message": "ERROR_MESSAGE"
  }
}
```

## 주요 에러 코드

| error.name | 발생 이유 |
| --- | --- |
| `INVALID_AUTH` | 인증 정보 누락 또는 인증 토큰 검증 실패 |
| `WRONG_FORMAT` | 요청 형식 위반 |
| `NO_TICKET` | 티켓 필드 누락 |
| `NO_TYPE` | 타입 필드 누락 |
| `NO_CODES` | 코드 필드 누락 |
| `INVALID_PARAM` | 필수 파라미터 누락 또는 지원하지 않는 값 요청 |

## 구현 체크리스트

- Private WebSocket은 JWT 인증 헤더를 지원하는 클라이언트를 사용한다.
- 연결 직후 ticket object와 data type object를 포함한 JSON Array를 전송한다.
- 장시간 연결은 ping/pong 또는 `"PING"` 메시지로 유지한다.
- 재연결 시 연결 요청 제한을 넘지 않도록 백오프한다.
- 대량 구독은 `SIMPLE`, `JSON_LIST`, `SIMPLE_LIST` 포맷으로 트래픽을 줄일 수 있는지 검토한다.
