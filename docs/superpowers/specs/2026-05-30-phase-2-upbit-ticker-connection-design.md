# Phase 2 Upbit ticker 최소 연결 설계

작성일: 2026-05-30

## 목적

Phase 2의 목적은 FastAPI 백엔드 코드가 실제 Upbit 공개 Quotation endpoint와 안정적으로 통신할 수 있는지 검증하는 것이다.

이 단계에서는 `KRW-BTC`, `KRW-ETH` ticker를 Upbit WebSocket에서 실제 수신하고, Phase 1에서 정의한 `UpbitTickerMessage`와 `TickerData` 계약으로 변환한 뒤 로그로 확인한다. 프론트엔드 연결, 브라우저 WebSocket, 전체 KRW Market 확장, trade/orderbook/candle 상세 구독은 이후 Phase에서 처리한다.

## 근거 문서

- `CONTEXT.md`: Market, Quotation data, Ticker event, Message envelope 용어.
- `docs/development-sequence.md`: Phase 2 목표와 완료 기준.
- `docs/adr/0001-root-local-command-entrypoint.md`: repository root는 `Makefile` 기반 로컬 명령 진입점으로 사용한다.
- `docs/adr/0003-rest-bff-and-direct-websocket.md`: REST는 Next.js BFF, WebSocket은 FastAPI 직접 연결.
- `docs/adr/0004-process-memory-for-mvp-state.md`: MVP 상태는 FastAPI 프로세스 메모리에 저장.
- `docs/adr/0005-quotation-only-mvp-boundary.md`: MVP는 공개 Quotation data만 사용.
- `docs/adr/0006-api-contract-envelope-and-model-source.md`: Phase 1 계약 모델과 Message envelope 정책.
- `docs/superpowers/specs/2026-05-30-phase-1-api-contracts-design.md`: ticker raw 모델과 mapper 정책.
- `docs/upbit/api/websocket-guide.md`: Upbit WebSocket endpoint, 요청 구조, idle timeout, 에러 형식.
- `docs/upbit/api/websocket/ticker.md`: ticker 구독 요청과 응답 필드.
- `docs/upbit/api/rate-limits.md`: WebSocket 연결/메시지 요청 제한.

## 범위

### 포함

- Upbit 공개 WebSocket endpoint `wss://api.upbit.com/websocket/v1` 연결.
- `KRW-BTC`, `KRW-ETH` ticker 구독.
- Upbit WebSocket ticker 구독 메시지 생성.
- 수신 payload JSON 파싱.
- `UpbitTickerMessage` validation.
- `UpbitTickerMessage -> TickerData` mapper 호출.
- ticker 수신 로그 출력.
- 연결 종료 또는 예외 발생 시 reconnect/backoff.
- FastAPI lifespan startup에서 ticker stream 자동 시작.
- `UPBIT_WS_ENABLED=false`일 때 자동 시작 생략.
- FastAPI 없이 실행 가능한 Upbit 연결 smoke command.
- smoke command에서 Upbit 공개 REST API 1회 호출로 REST 접근성 확인.
- repository root `Makefile`에서 Phase 2 실행 명령 제공.
- 네트워크 없이 실행되는 단위 테스트.

### 제외

- 수신 ticker를 `MarketState`에 저장하는 기능.
- `GET /api/snapshot` endpoint 구현.
- Backend -> Frontend WebSocket endpoint 구현.
- Next.js BFF Route Handler 구현.
- 프론트 UI 또는 프론트 WebSocket client 구현.
- 전체 KRW Market ticker 구독.
- selected-market trade/orderbook/candle 상세 구독.
- Alert event 생성.
- Redis, DB, 인증 API, 주문 API.
- root-level `package.json`, root-level `pnpm-workspace.yaml`, root-level Upbit dashboard `pyproject.toml`.

## 설계 원칙

Phase 2는 데이터 파이프라인의 첫 외부 연결 리스크를 제거하는 단계다. 따라서 구현은 작게 유지하되, smoke command와 FastAPI lifecycle이 서로 다른 방식으로 Upbit에 붙지 않도록 공통 연결 흐름을 공유한다.

문제 발생 시 원인을 다음처럼 분리할 수 있어야 한다.

```text
smoke command도 실패
  -> Upbit endpoint, 네트워크, 구독 메시지, raw payload, mapper 문제

smoke command는 성공하지만 FastAPI 실행에서 실패
  -> FastAPI lifespan, background task, shutdown 처리 문제
```

## 구성

### `Makefile`

역할:

- repository root에서 Phase 2에 필요한 로컬 명령을 짧게 실행한다.
- 실제 런타임은 각 앱 디렉터리의 도구를 사용한다.
- backend 명령은 `cd apps/backend && ...` 형태로 `uv`를 호출한다.
- root에 새 Node/Python workspace를 만들지 않는다.

Phase 2에서 제공할 target:

```makefile
.PHONY: upbit-smoke dev-api dev-api-no-upbit test-api

upbit-smoke
	cd apps/backend && uv run python -m upbit_dashboard.tools.smoke_upbit_connection

dev-api
	cd apps/backend && uv run uvicorn upbit_dashboard.main:app --reload

dev-api-no-upbit
	cd apps/backend && UPBIT_WS_ENABLED=false uv run uvicorn upbit_dashboard.main:app --reload

test-api
	cd apps/backend && uv run pytest
```

### `upbit_dashboard.upbit.client`

역할:

- Upbit WebSocket endpoint에 연결한다.
- ticker 구독 메시지를 만든다.
- WebSocket 수신 payload를 JSON object로 파싱한다.
- Upbit 에러 payload와 ticker payload를 구분한다.
- ticker payload를 `UpbitTickerMessage`로 검증한다.
- 검증된 raw message를 `TickerData`로 변환한다.

이 모듈은 reconnect loop를 직접 소유하지 않는다. 단일 연결과 단일 메시지 처리에 집중한다.

### `upbit_dashboard.upbit.runner`

역할:

- `client`를 사용해 ticker stream을 반복 실행한다.
- 연결이 끊기거나 예외가 발생하면 backoff 후 재연결한다.
- 종료 signal을 받으면 loop를 멈춘다.
- 수신한 `TickerData`를 callback으로 전달하거나 로그로 출력한다.

Phase 2에서는 callback의 기본 동작을 로그 출력으로 둔다. Phase 3에서 `MarketState.upsert_ticker()`를 callback으로 연결할 수 있다.

### `upbit_dashboard.tools.smoke_upbit_connection`

역할:

- FastAPI 서버 없이 수동으로 실행된다.
- Upbit 공개 REST API `https://api.upbit.com/v1/market/all?is_details=false`를 1회 호출해 REST 접근성을 확인한다.
- Upbit WebSocket에 연결해 `KRW-BTC`, `KRW-ETH` ticker를 수신한다.
- 각 Market의 ticker가 최소 1회씩 수신되면 성공으로 종료한다.
- 15초 안에 필요한 ticker를 모두 받지 못하면 실패로 종료한다.

예상 실행 명령:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
make upbit-smoke
```

### `upbit_dashboard.main`

역할:

- FastAPI lifespan startup에서 ticker runner를 background task로 시작한다.
- 서버 종료 시 background task를 정리한다.
- `UPBIT_WS_ENABLED=false`이면 Upbit WebSocket 자동 연결을 시작하지 않는다.

기본 정책은 자동 연결 ON이다.

```text
UPBIT_WS_ENABLED unset
  -> 자동 연결 ON

UPBIT_WS_ENABLED=true
  -> 자동 연결 ON

UPBIT_WS_ENABLED=false
  -> 자동 연결 OFF
```

## Upbit 구독 정책

Phase 2의 구독 Market은 고정값으로 둔다.

```text
KRW-BTC
KRW-ETH
```

구독 메시지는 Upbit DEFAULT 포맷을 사용한다.

```json
[
  {"ticket": "upbit-dashboard-phase2"},
  {"type": "ticker", "codes": ["KRW-BTC", "KRW-ETH"]},
  {"format": "DEFAULT"}
]
```

`SIMPLE`, `JSON_LIST`, `SIMPLE_LIST`는 Phase 8의 전체 KRW Market 확장 시점에 트래픽 최적화가 필요하면 검토한다.

## 데이터 흐름

### smoke command

```text
make upbit-smoke
  -> Upbit REST market endpoint 1회 호출
  -> Upbit WebSocket 연결
  -> ticker 구독 메시지 전송
  -> bytes 또는 str payload 수신
  -> JSON object 파싱
  -> UpbitTickerMessage validation
  -> TickerData 변환
  -> KRW-BTC, KRW-ETH 수신 확인
  -> smoke ok 로그 출력 후 종료
```

### FastAPI lifespan

```text
make dev-api
  -> lifespan startup
  -> UPBIT_WS_ENABLED 확인
  -> ticker runner background task 시작
  -> Upbit WebSocket 연결
  -> ticker 구독 메시지 전송
  -> TickerData 변환
  -> ticker 수신 로그 출력
  -> 연결 종료 시 backoff 후 reconnect
```

## reconnect/backoff 정책

Phase 2에서는 단순한 exponential backoff를 사용한다.

```text
초기 대기: 1초
실패 시 증가: 직전 대기 시간의 2배
최대 대기: 30초
정상 연결 후 끊김: 다시 1초부터 시작
```

연결 또는 구독 메시지를 과도하게 반복하지 않아야 한다. Upbit 문서의 WebSocket 제한은 다음과 같다.

```text
websocket-connect: 초당 최대 5회
websocket-message: 초당 최대 5회, 분당 100회
```

backoff는 이 제한을 넘지 않도록 하는 최소 보호장치다.

## ping/idle timeout 정책

Upbit 문서상 서버는 120초 동안 데이터 송수신이 없으면 idle timeout으로 연결을 종료할 수 있다.

Phase 2에서는 `websockets` 클라이언트의 기본 ping/pong 기능을 우선 사용한다. 별도의 `"PING"` text message 전송은 구현하지 않는다.

이유:

- ticker stream은 정상 상황에서 지속적으로 이벤트가 들어온다.
- 클라이언트 라이브러리의 ping/pong이 연결 유지의 기본 수단이다.
- `"PING"` text message는 Upbit 특화 fallback이므로 필요성이 확인되면 Phase 14 연결 안정성에서 추가한다.

## 로그 정책

Phase 2 로그는 사람이 연결 성공 여부를 확인할 수 있을 만큼만 출력한다. ticker가 많이 들어와도 로그가 과도하게 커지지 않도록 Market별 수신 로그를 제한하거나 샘플링할 수 있다.

예상 로그:

```text
INFO Upbit ticker stream starting markets=KRW-BTC,KRW-ETH
INFO Upbit WS connected endpoint=wss://api.upbit.com/websocket/v1
INFO Upbit ticker received market=KRW-BTC tradePrice=108359000 streamType=REALTIME
INFO Upbit ticker received market=KRW-ETH tradePrice=4200000 streamType=REALTIME
WARNING Upbit WS disconnected; reconnecting in 2.0s
ERROR Upbit WS message validation failed market=KRW-BTC error=...
```

## 에러 처리

### Upbit WebSocket 에러 payload

Upbit WebSocket 에러는 다음 구조를 가진다.

```json
{
  "error": {
    "name": "ERROR_CODE",
    "message": "ERROR_MESSAGE"
  }
}
```

Phase 2에서는 이 payload를 ticker로 validation하지 않고, Upbit WebSocket 에러로 로그에 남긴다. 이 에러를 프론트 WebSocket `type: "error"` envelope로 전달하는 것은 Backend -> Frontend WebSocket endpoint가 생기는 이후 Phase에서 처리한다.

### validation 실패

ticker처럼 보이는 payload라도 `UpbitTickerMessage` 필수 필드가 없거나 enum 값이 맞지 않으면 validation 실패로 처리한다.

Phase 2에서는 validation 실패를 로그로 남기고 stream 자체는 계속 유지한다. 단일 메시지 오류가 전체 연결을 종료시키지 않도록 한다.

### 연결 실패

연결 실패, 정상 종료, 예외 종료는 runner가 backoff 후 재연결한다. 서버 shutdown으로 인한 종료는 재연결하지 않는다.

## 설정

Phase 2에서 필요한 설정은 최소화한다.

| 설정 | 기본값 | 설명 |
| --- | --- | --- |
| `UPBIT_WS_ENABLED` | `true` | FastAPI startup 시 Upbit ticker stream 자동 시작 여부 |

나머지 값은 Phase 2 코드 상수로 둔다.

| 값 | Phase 2 기본값 |
| --- | --- |
| WebSocket endpoint | `wss://api.upbit.com/websocket/v1` |
| REST smoke endpoint | `https://api.upbit.com/v1/market/all?is_details=false` |
| Markets | `KRW-BTC`, `KRW-ETH` |
| WebSocket format | `DEFAULT` |
| Initial backoff | `1s` |
| Max backoff | `30s` |
| Smoke timeout | `15s` |

전체 KRW Market, endpoint override, 더 세밀한 timeout 설정은 필요성이 생기면 별도 Phase에서 추가한다.

## 테스트 계획

자동 테스트는 외부 Upbit 네트워크에 의존하지 않는다.

### 구독 메시지 생성 테스트

검증:

- ticket object가 포함된다.
- data type object의 `type`은 `ticker`다.
- `codes`에는 `KRW-BTC`, `KRW-ETH`가 포함된다.
- format object의 `format`은 `DEFAULT`다.

### 수신 메시지 처리 테스트

검증:

- bytes payload를 JSON으로 파싱한다.
- ticker JSON object를 `UpbitTickerMessage`로 validation한다.
- validation된 raw message를 `TickerData`로 변환한다.
- 변환 결과는 Phase 1 `TickerData` camelCase 직렬화 계약과 호환된다.

### 잘못된 메시지 처리 테스트

검증:

- Upbit error payload는 ticker message로 처리하지 않는다.
- 필수 필드가 빠진 ticker payload는 validation error로 처리된다.
- JSON object가 아닌 payload는 메시지 처리 실패로 분리된다.

### 설정 테스트

검증:

- `UPBIT_WS_ENABLED`가 없으면 자동 연결 enabled로 판단한다.
- `UPBIT_WS_ENABLED=true`면 자동 연결 enabled로 판단한다.
- `UPBIT_WS_ENABLED=false`면 자동 연결 disabled로 판단한다.

## 수동 검증 계획

### smoke command

명령:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
make upbit-smoke
```

성공 기준:

```text
REST market check ok
WS connected
ticker received market=KRW-BTC ...
ticker received market=KRW-ETH ...
smoke ok
```

### FastAPI 자동 연결

명령:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
make dev-api
```

성공 기준:

```text
Upbit ticker stream starting markets=KRW-BTC,KRW-ETH
Upbit ticker received market=KRW-BTC ...
Upbit ticker received market=KRW-ETH ...
```

### 자동 연결 비활성화

명령:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
make dev-api-no-upbit
```

성공 기준:

```text
Upbit ticker stream disabled by UPBIT_WS_ENABLED=false
```

이 경우 `/health`는 기존처럼 응답해야 한다.

## 구현 순서

1. `apps/backend`에 WebSocket 클라이언트 의존성을 명시한다.
2. Upbit ticker 구독 메시지 생성 함수를 작성한다.
3. WebSocket payload 파싱과 ticker 변환 함수를 작성한다.
4. 단일 연결을 수행하는 client 함수를 작성한다.
5. reconnect/backoff를 담당하는 runner를 작성한다.
6. `UPBIT_WS_ENABLED` 설정 판별 함수를 작성한다.
7. smoke command를 작성한다.
8. FastAPI lifespan startup/shutdown에 runner background task를 연결한다.
9. root `Makefile`에 `upbit-smoke`, `dev-api`, `dev-api-no-upbit`, `test-api` target을 추가한다.
10. 네트워크 없는 단위 테스트를 작성한다.
11. `make test-api`로 단위 테스트를 실행한다.
12. `make upbit-smoke`로 실제 Upbit REST/WS 연결을 수동 검증한다.
13. `make dev-api` 로그로 자동 연결을 수동 검증한다.

## 완료 기준

- smoke command에서 Upbit 공개 REST API 접근이 확인된다.
- smoke command에서 `KRW-BTC`, `KRW-ETH` ticker가 실제 수신된다.
- 수신 ticker가 `UpbitTickerMessage` validation과 `TickerData` mapper를 통과한다.
- FastAPI startup에서 Upbit ticker stream이 기본 자동 시작된다.
- `UPBIT_WS_ENABLED=false`이면 FastAPI startup에서 Upbit 연결을 생략한다.
- root `Makefile`에서 `upbit-smoke`, `dev-api`, `dev-api-no-upbit`, `test-api` target을 제공한다.
- 연결 종료 또는 예외 발생 시 backoff 후 재연결을 시도한다.
- 자동 테스트는 외부 네트워크 없이 통과한다.
- Phase 3에서 `TickerData`를 `MarketState`에 저장할 수 있도록 runner 출력 경계가 명확하다.
