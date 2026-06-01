# Phase 3 Backend 메모리 상태 저장 설계

작성일: 2026-06-01

## 목적

Phase 3의 목적은 Phase 2에서 수신한 Upbit ticker를 FastAPI backend 프로세스 메모리의 `MarketState`에 저장하고, REST `GET /api/snapshot`으로 최신 상태를 조회할 수 있게 만드는 것이다.

이 단계가 끝나면 새 프론트엔드 사용자가 접속했을 때 실시간 WebSocket 이벤트를 기다리지 않고도 backend가 이미 보유한 최신 ticker snapshot을 먼저 받을 수 있어야 한다.

## 근거 문서

- `CONTEXT.md`: Market, Ticker event, MarketState, Snapshot, Message envelope 용어.
- `docs/development-sequence.md`: Phase 3 목표와 완료 기준.
- `docs/adr/0003-rest-bff-and-direct-websocket.md`: REST는 Next.js BFF, WebSocket은 FastAPI 직접 연결.
- `docs/adr/0004-process-memory-for-mvp-state.md`: MVP 상태는 FastAPI backend 프로세스 메모리에 저장.
- `docs/adr/0005-quotation-only-mvp-boundary.md`: MVP는 공개 Quotation data만 사용.
- `docs/adr/0006-api-contract-envelope-and-model-source.md`: REST Message envelope와 Pydantic 계약 모델 정책.
- `docs/superpowers/specs/2026-05-30-phase-1-api-contracts-design.md`: `TickerData`, `MarketStateSnapshotResponse` 계약.
- `docs/superpowers/specs/2026-05-30-phase-2-upbit-ticker-connection-design.md`: Upbit ticker runner와 `on_ticker` callback 경계.

## 범위

### 포함

- FastAPI app state에 생성된 `MarketState`를 runtime ticker stream과 연결.
- Upbit ticker 수신 시 `MarketState.upsert_ticker()` 호출.
- Phase 2의 ticker 수신 logging 유지.
- `GET /api/snapshot` FastAPI endpoint 구현.
- `MarketStateSnapshotResponse` envelope로 snapshot 응답 반환.
- 빈 `MarketState`도 `200 OK`와 빈 `tickers` 배열로 응답.
- 네트워크 없는 단위 테스트와 FastAPI route 테스트.

### 제외

- Next.js BFF Route Handler 구현.
- Frontend WebSocket client 구현.
- Backend -> Frontend WebSocket endpoint 구현.
- 전체 KRW Market ticker 확장.
- `trade`, `orderbook`, `candle` 상세 데이터 저장.
- Detail subscription 관리.
- Alert event 생성.
- Redis, DB, cache, persistence 추가.
- 새로운 REST 계약 필드 추가.

## 현재 상태

이미 존재하는 기반:

- `upbit_dashboard.state.market_state.MarketState`
- `MarketState.upsert_ticker()`
- `MarketState.snapshot()`
- `upbit_dashboard.contracts.rest.MarketStateSnapshotResponse`
- `upbit_dashboard.contracts.rest.MarketStateSnapshotData`
- `upbit_dashboard.contracts.quotation.TickerData`
- `upbit_dashboard.upbit.runner.run_ticker_stream()`
- `run_ticker_stream(..., on_ticker=...)` callback 경계

Phase 3에서 새로 정의할 핵심은 데이터 모델이 아니라 runtime wiring과 REST endpoint다.

## 설계 원칙

Phase 3는 backend 내부의 상태 흐름을 완성하는 단계다. Upbit WebSocket 연결, raw payload parsing, `TickerData` mapper, REST envelope 계약은 이전 Phase에서 이미 다룬다.

따라서 이 Phase에서는 다음 흐름만 작게 고정한다.

```text
Upbit ticker 수신
  -> TickerData 변환
  -> MarketState.upsert_ticker()
  -> GET /api/snapshot
  -> MarketStateSnapshotResponse
```

## 구성

### `upbit_dashboard.main`

역할:

- FastAPI app 생성 시 `app.state.market_state = MarketState()`를 유지한다.
- lifespan startup에서 ticker stream을 시작할 때 `on_ticker` handler를 넘긴다.
- `on_ticker` handler는 `MarketState` 업데이트와 ticker 수신 logging을 모두 수행한다.

정책:

- Phase 2의 `log_ticker()` 동작은 제거하지 않는다.
- `on_ticker`를 `MarketState.upsert_ticker`로 단순 교체하지 않는다.
- `MarketState` 업데이트 후 `log_ticker()`를 호출하는 합성 handler를 사용한다.

예상 흐름:

```text
handle_ticker(ticker)
  -> app.state.market_state.upsert_ticker(ticker)
  -> log_ticker(ticker)
```

### `upbit_dashboard.state.market_state`

역할:

- Market별 최신 `TickerData`를 프로세스 메모리에 보관한다.
- 같은 Market ticker가 다시 들어오면 최신 값으로 교체한다.
- snapshot 요청 시 현재 보유한 ticker 목록을 반환한다.

정책:

- Phase 3에서는 `TickerData`만 저장한다.
- 정렬 정책은 넣지 않는다. Market List 정렬은 Phase 8에서 다룬다.
- 상태는 backend 프로세스 재시작 시 초기화된다. 이는 ADR-0004의 MVP process memory 결정과 일치한다.

### `upbit_dashboard.api.routes.snapshot`

역할:

- `GET /api/snapshot` endpoint를 제공한다.
- `request.app.state.market_state`에서 현재 snapshot을 읽는다.
- `MarketStateSnapshotResponse`로 응답한다.

응답 정책:

- HTTP status는 정상 조회 시 항상 `200 OK`다.
- ticker가 아직 없으면 `tickers: []`를 반환한다.
- REST 성공 응답은 `type`, `timestamp`, `data` Message envelope를 사용한다.
- `type`은 `market-state:snapshot`이다.

예상 응답:

```json
{
  "type": "market-state:snapshot",
  "timestamp": "2026-06-01T03:00:00Z",
  "data": {
    "generatedAt": "2026-06-01T03:00:00Z",
    "tickers": []
  }
}
```

## Timestamp 정책

새 timestamp 필드는 만들지 않는다. Phase 1 Pydantic 계약의 `description`을 기준으로 기존 필드를 사용한다.

| 필드 | 의미 |
| --- | --- |
| `MarketStateSnapshotResponse.timestamp` | 우리 서버가 REST 응답을 만든 시각 |
| `MarketStateSnapshotData.generatedAt` | backend `MarketState` snapshot 생성 시각 |
| `TickerData.timestampMs` | Upbit ticker 이벤트 타임스탬프 |
| `TickerData.tradeTimestampMs` | Upbit ticker 체결 타임스탬프 |

`GET /api/snapshot`에서는 응답 생성 시점의 UTC `now`를 만들고, 같은 값을 envelope `timestamp`와 `data.generatedAt`에 사용한다. 이렇게 하면 `generatedAt`은 마지막 ticker 갱신 시각이 아니라 snapshot 생성 시각이라는 계약 설명과 일치한다.

Upbit 원본 시각은 각 ticker 내부의 `timestampMs`, `tradeTimestampMs`를 그대로 사용한다.

## Logging 정책

Phase 3에서도 Phase 2의 ticker 수신 로그는 유지한다.

이유:

- `KRW-BTC`, `KRW-ETH` 최소 구독 단계에서는 수신 여부를 로그로 확인하는 가치가 크다.
- MarketState 업데이트와 Upbit 수신 로그는 서로 다른 관찰 지점이다.
- `on_ticker`가 하나뿐이므로 handler 합성으로 둘 다 수행한다.

예상 로그:

```text
INFO Upbit ticker received market=KRW-BTC tradePrice=108359000 streamType=REALTIME
INFO Upbit ticker received market=KRW-ETH tradePrice=4200000 streamType=REALTIME
```

전체 KRW Market으로 확장하는 Phase 8 이후에는 ticker 로그 샘플링 또는 요약 로그 전환을 검토한다.

## 에러 처리

### snapshot 조회

`MarketState`가 비어 있는 것은 오류가 아니다. 서버 시작 직후 또는 `UPBIT_WS_ENABLED=false` 실행 중에도 `/api/snapshot`은 정상 응답해야 한다.

```json
{
  "type": "market-state:snapshot",
  "data": {
    "tickers": []
  }
}
```

### ticker handler 실패

`MarketState.upsert_ticker()` 또는 handler 내부에서 예외가 발생하면 `run_ticker_stream()`의 기존 reconnect/backoff 경계가 처리한다. Phase 3에서는 별도 retry queue나 dead-letter 처리를 추가하지 않는다.

## 데이터 흐름

### FastAPI startup

```text
create_app()
  -> app.state.market_state = MarketState()
  -> include api_router

lifespan startup
  -> UPBIT_WS_ENABLED 확인
  -> run_ticker_stream(..., on_ticker=handle_ticker) background task 생성
```

### ticker 수신

```text
Upbit WebSocket payload
  -> UpbitTickerMessage validation
  -> TickerData mapper
  -> run_ticker_stream on_ticker callback
  -> MarketState.upsert_ticker(ticker)
  -> log_ticker(ticker)
```

### snapshot 조회

```text
GET /api/snapshot
  -> request.app.state.market_state
  -> now = datetime.now(timezone.utc)
  -> MarketState.snapshot(generated_at=now)
  -> MarketStateSnapshotResponse(timestamp=now, data=...)
```

## 테스트 계획

자동 테스트는 외부 Upbit 네트워크에 의존하지 않는다.

### MarketState 테스트

검증:

- `upsert_ticker()`가 Market별 최신 ticker를 저장한다.
- 같은 Market을 다시 저장하면 최신 값으로 교체한다.
- `snapshot()`이 현재 ticker 목록을 반환한다.
- `generated_at`을 명시하면 snapshot에 그 값이 사용된다.

### snapshot route 테스트

검증:

- 빈 상태에서 `GET /api/snapshot`은 `200 OK`를 반환한다.
- 빈 상태 응답의 `type`은 `market-state:snapshot`이다.
- 빈 상태 응답의 `data.tickers`는 빈 배열이다.
- MarketState에 ticker를 미리 넣으면 응답 `tickers[]`에 포함된다.
- 응답 JSON은 camelCase alias를 사용한다.
- `tickers[]` 항목은 `TickerData` 직렬화 shape과 동일하다.

### lifespan wiring 테스트

검증:

- `run_ticker_stream()`에 `on_ticker` handler가 전달된다.
- 전달된 handler를 호출하면 `app.state.market_state`가 업데이트된다.
- handler 호출 시 기존 `log_ticker()`도 호출된다.
- `UPBIT_WS_ENABLED=false`이면 기존처럼 ticker stream을 시작하지 않는다.

## 수동 검증 계획

### Upbit 자동 연결 비활성화 상태

명령:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
make dev-api-no-upbit
```

확인:

```bash
curl http://localhost:8000/api/snapshot
```

성공 기준:

```text
HTTP 200
type == market-state:snapshot
data.tickers == []
```

### Upbit 자동 연결 상태

명령:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
make dev-api
```

확인:

```bash
curl http://localhost:8000/api/snapshot
```

성공 기준:

```text
HTTP 200
data.tickers includes KRW-BTC or KRW-ETH after ticker 수신
backend log still shows Upbit ticker received ...
```

## 구현 순서

1. `/api/snapshot` route 테스트를 작성한다.
2. `apps/backend/src/upbit_dashboard/api/routes/snapshot.py`를 추가한다.
3. `api_router`에 snapshot router를 등록한다.
4. lifespan wiring 테스트를 작성한다.
5. `main.py`에서 `handle_ticker` 합성 handler를 추가하고 `run_ticker_stream(..., on_ticker=handle_ticker)`로 연결한다.
6. `MarketState.snapshot(generated_at=...)` 동작을 필요한 범위에서 테스트로 보강한다.
7. backend test suite를 실행한다.
8. `make dev-api-no-upbit` 상태에서 `/api/snapshot` 빈 응답을 수동 확인한다.
9. `make dev-api` 상태에서 ticker 수신 후 `/api/snapshot`에 ticker가 포함되는지 수동 확인한다.

## 완료 기준

- Upbit ticker 수신 시 backend `MarketState`가 업데이트된다.
- Phase 2의 ticker 수신 logging이 유지된다.
- `GET /api/snapshot`이 `MarketStateSnapshotResponse` envelope로 응답한다.
- ticker가 없는 상태에서도 `/api/snapshot`은 `200 OK`와 빈 `tickers` 배열을 반환한다.
- ticker가 있는 상태에서는 `/api/snapshot`이 최신 `TickerData` 목록을 반환한다.
- `generatedAt`은 snapshot 생성 시각으로 채워진다.
- 자동 테스트는 외부 네트워크 없이 통과한다.
