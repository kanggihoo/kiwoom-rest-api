# WebSocket - 내 자산(MyAsset)

출처: https://docs.upbit.com/kr/reference/websocket-myasset  
정리일: 2026-05-29

## 핵심 요약

내 자산 변동 이벤트를 WebSocket으로 구독한다. Exchange 데이터이므로 Private WebSocket Endpoint와 JWT 인증이 필요하다.

```text
wss://api.upbit.com/websocket/v1/private
```

## 전송 방식

- 실제 자산 변동이 발생할 때만 실시간 스트림이 전송된다.
- 연결 후 자산 변동이 없으면 데이터가 수신되지 않는 것이 정상이다.
- 내 자산 WebSocket 스트림을 계정에서 최초 구독하는 경우 자산 변동 여부와 상관없이 수분간 데이터 수신이 지연될 수 있다.
- 최초 1회 연결 이후에는 재연결 등을 통해 데이터 수신을 반드시 확인한 뒤 사용한다.

## Request Data Type Object

| 필드 | 타입 | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- | --- |
| `type` | String | 필수 | 없음 | `myAsset` |

`myAsset` 요청은 `codes` 파라미터를 지원하지 않는다. `codes`를 포함하면 `WRONG_FORMAT` 에러가 발생한다.

## 요청 예시

```json
[
  {"ticket": "unique-ticket"},
  {"type": "myAsset"}
]
```

JSON_LIST 포맷:

```json
[
  {"ticket": "unique-ticket"},
  {"type": "myAsset"},
  {"format": "JSON_LIST"}
]
```

## 주요 응답 필드

| 필드 | 축약형 | 설명 |
| --- | --- | --- |
| `type` | `ty` | 데이터 항목. `myAsset` |
| `asset_uuid` | `astuid` | 자산 고유 식별자 |
| `assets` | `ast` | 자산 목록 |
| `assets.currency` | `ast.cu` | 화폐 코드 |
| `assets.balance` | `ast.b` | 주문 가능 수량 |
| `assets.locked` | `ast.l` | 주문 중 묶여 있는 수량 |
| `asset_timestamp` | `asttms` | 자산 타임스탬프(ms) |
| `timestamp` | `tms` | 이벤트 타임스탬프(ms) |
| `stream_type` | `st` | `REALTIME` |

## 구현 체크리스트

- JWT 인증 헤더를 포함해 Private WebSocket에 연결한다.
- `codes`를 넣지 않는다.
- 최초 구독 시 몇 분간 이벤트가 없을 수 있으므로 초기 데이터는 REST 잔고 조회로 보강한다.
- 이벤트가 오면 `assets.currency` 단위로 잔고 캐시를 갱신한다.
- 이벤트 미수신 상태에서도 연결 유지 로직을 별도로 둔다.
