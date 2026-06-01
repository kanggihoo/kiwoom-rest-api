# Phase 8/10 Markets and Candles REST API 설계

작성일: 2026-06-01

## 목적

이 설계는 Phase 8의 전체 KRW Market 목록 확장과 Phase 10의 차트 초기/과거 candle 조회를 위해 FastAPI backend에 `GET /api/markets`, `GET /api/candles`를 추가하는 방향을 고정한다.

Phase 8/10이 끝나면 frontend는 같은 origin의 Next.js BFF를 통해 Market 메타데이터와 candle history를 조회하고, FastAPI는 Upbit Quotation REST API를 호출해 기존 Message envelope 계약으로 응답해야 한다.

## 근거 문서

- `CONTEXT.md`: Market, KRW Market, Market List, Candle event, Candle Unit, BFF, Message envelope 용어.
- `docs/development-sequence.md`: Phase 8 전체 KRW ticker 확장, Phase 10 차트 초기/과거 데이터.
- `docs/adr/0002-bff-upstream-error-handling.md`: Next.js BFF upstream error handling 공통화.
- `docs/adr/0003-rest-bff-and-direct-websocket.md`: REST는 Next.js BFF, WebSocket은 FastAPI 직접 연결.
- `docs/adr/0004-process-memory-for-mvp-state.md`: MVP 상태는 FastAPI 프로세스 메모리에 저장.
- `docs/adr/0005-quotation-only-mvp-boundary.md`: MVP는 공개 Quotation data만 사용.
- `docs/adr/0006-api-contract-envelope-and-model-source.md`: REST Message envelope와 Pydantic 계약 모델 정책.
- `docs/upbit/api/quotation/trading-pairs.md`: Upbit Market 목록 REST API.
- `docs/upbit/api/quotation/candles.md`: Upbit candle REST API와 지원 단위.
- `docs/upbit/api/rate-limits.md`: Upbit REST rate limit, 429, 418, `Remaining-Req`.
- `docs/upbit/api/rest-api-guide.md`: REST error response 형식과 status code.

## 범위

### 포함

- FastAPI `GET /api/markets` endpoint.
- FastAPI `GET /api/candles` endpoint.
- Next.js `GET /api/markets`, `GET /api/candles` BFF Route Handler 설계.
- Upbit REST Market 목록 adapter.
- Upbit REST candle adapter.
- KRW Market 필터링.
- `MarketSummary`, `MarketsListResponse`, `Candle`, `CandlesListResponse` 기존 계약 사용.
- `/api/markets` 10분 process-memory cache.
- `/api/candles` query validation, Upbit unit mapping, 응답 정렬.
- Upbit REST error를 기존 error envelope로 매핑.
- backend route/service/adapter 테스트와 BFF 최소 forwarding 테스트.

### 제외

- Frontend Market List UI 구현.
- Frontend chart UI 구현.
- Zustand store 구현.
- WebSocket `candle:update` 실시간 반영.
- 선택 Market detail subscription 관리.
- Redis, DB, 외부 cache backend.
- candle response cache.
- Upbit 인증 API.
- 실제 주문 기능.

## 전체 구조

FastAPI가 Upbit Quotation REST API 연동과 데이터 정규화의 소유자가 된다. Next.js BFF는 브라우저에 같은 origin REST endpoint를 제공하고 FastAPI 응답을 전달한다.

```text
Browser
  -> Next.js BFF /api/markets
  -> FastAPI /api/markets
  -> Upbit REST /v1/market/all
```

```text
Browser
  -> Next.js BFF /api/candles
  -> FastAPI /api/candles
  -> Upbit REST /v1/candles/...
```

Next.js BFF에는 별도 `revalidate`나 cache를 두지 않는다. Cache 정책은 Upbit 호출 책임을 가진 FastAPI에 둔다.

## `/api/markets`

### 목적

`GET /api/markets`는 frontend가 Market List의 기본 행을 구성하기 위한 KRW Market 메타데이터를 반환한다.

이 endpoint는 가격, 등락률, 24시간 거래대금을 반환하지 않는다. 그 값은 기존 `/api/snapshot`과 WebSocket `ticker:update`에서 `market` 코드 기준으로 병합한다.

### 응답 계약

기존 `MarketsListResponse`를 사용한다.

```json
{
  "type": "markets:list",
  "timestamp": "2026-06-01T00:00:00Z",
  "data": {
    "markets": [
      {
        "market": "KRW-BTC",
        "koreanName": "비트코인",
        "englishName": "Bitcoin",
        "quoteCurrency": "KRW",
        "baseCurrency": "BTC"
      }
    ]
  }
}
```

### Upbit 호출

FastAPI는 다음 Upbit endpoint를 호출한다.

```http
GET https://api.upbit.com/v1/market/all?is_details=false
```

Upbit 응답에서 `market`이 `KRW-`로 시작하는 Market만 `MarketSummary`로 변환한다.

변환 규칙:

| 앱 필드 | Upbit 원본 | 설명 |
| --- | --- | --- |
| `market` | `market` | Upbit Market 코드 |
| `koreanName` | `korean_name` | 한글 Market 이름 |
| `englishName` | `english_name` | 영문 Market 이름 |
| `quoteCurrency` | `market` parsing | `KRW-BTC`의 `KRW` |
| `baseCurrency` | `market` parsing | `KRW-BTC`의 `BTC` |

### Cache 정책

`/api/markets`는 FastAPI 프로세스 메모리에 10분 TTL cache를 둔다.

정책:

- TTL 기본값은 600초다.
- Next.js BFF에는 별도 cache/revalidation을 두지 않는다.
- Cache 구현은 별도 dependency 없이 직접 구현한다.
- Cache는 FastAPI app state 또는 service instance가 보유한다.
- `asyncio.Lock` 하나로 refresh 중복을 막는다.
- `threading.Lock`이나 `RLock`을 잡은 상태에서 `await`하지 않는다.
- TTL이 만료되어도 마지막 성공값은 stale 값으로 보관한다.
- Upbit refresh 실패 시 stale 값이 있으면 stale 값을 성공 응답으로 반환한다.
- Upbit refresh 실패 시 stale 값도 없으면 error envelope를 반환한다.

예상 service 흐름:

```text
list_krw_markets()
  -> fresh cache가 있으면 반환
  -> refresh_lock 획득
  -> fresh cache 재확인
  -> Upbit /v1/market/all 호출
  -> KRW Market 필터링
  -> cache replace
  -> 반환
```

실패 흐름:

```text
Upbit refresh 실패
  -> stale cache가 있으면 stale markets 반환
  -> stale cache가 없으면 DashboardApiError 발생
```

### Phase 8 전체 KRW ticker 구독과의 관계

Phase 8의 전체 KRW ticker WebSocket 구독도 같은 KRW Market 목록을 필요로 한다. 따라서 `/api/markets`만을 위한 별도 Upbit caller를 만들지 않고, Market 목록 조회와 KRW 필터링은 재사용 가능한 service로 둔다.

정책:

- `MarketCatalogueService`는 `/api/markets` endpoint와 ticker subscription 확장에서 함께 사용할 수 있게 둔다.
- Backend startup에서 전체 KRW ticker 구독을 구성할 때도 같은 service의 KRW Market 목록을 사용한다.
- 전체 KRW ticker subscription을 구성하는 동안 Upbit Market 목록 조회가 실패하고 stale cache가 없으면, runner는 기존 reconnect/backoff 정책을 따라 재시도한다.
- `/api/markets`의 10분 cache는 브라우저 응답과 backend 내부 subscription 목록 구성에 같은 원천을 제공한다.
- `UPBIT_TICKER_MARKETS`가 명시된 경우에는 개발/테스트 편의를 위해 설정값 구독을 우선할 수 있다. 전체 KRW 자동 구독 전환 여부는 implementation plan에서 설정 이름과 기본값을 고정한다.

## `/api/candles`

### 목적

`GET /api/candles`는 선택 Market 차트의 초기 candle history와 과거 pagination을 위한 OHLCV 목록을 반환한다.

이번 범위에서는 REST 방식만 처리한다. WebSocket `candle:update`로 마지막 candle을 실시간 갱신하는 작업은 Phase 11에서 다룬다.

### 요청 계약

```http
GET /api/candles?market=KRW-BTC&unit=1m
GET /api/candles?market=KRW-BTC&unit=1m&count=200&to=2026-06-01T09:00:00Z
```

Query parameters:

| 이름 | 필수 | 정책 |
| --- | --- | --- |
| `market` | 예 | KRW Market만 허용 |
| `unit` | 예 | `1m`, `5m`, `15m`, `30m`, `1h`, `1d`, `1w` |
| `count` | 아니오 | 기본 200, 최대 200 |
| `to` | 아니오 | 이 시각 이전 candle 조회 기준 |

`to`가 없으면 Upbit은 현재 요청 시점 기준 최신 candle을 반환한다. `to`가 있으면 해당 시각 이전의 candle을 과거 방향으로 조회한다.

스크롤 pagination 예:

```text
초기 응답:
09:00 ... 12:19

다음 과거 요청:
to=2026-06-01T09:00:00Z

추가 응답:
05:40 ... 08:59
```

Upbit candle은 체결이 없는 구간을 반환하지 않을 수 있으므로 `count=200`은 최대 200개로 해석한다.

### 응답 계약

기존 `CandlesListResponse`를 사용한다.

```json
{
  "type": "candles:list",
  "timestamp": "2026-06-01T00:00:00Z",
  "data": {
    "market": "KRW-BTC",
    "candleUnit": "1m",
    "candles": [
      {
        "candleDateTimeUtc": "2026-06-01T08:59:00",
        "candleDateTimeKst": "2026-06-01T17:59:00",
        "openingPrice": 100.0,
        "highPrice": 110.0,
        "lowPrice": 95.0,
        "tradePrice": 105.0,
        "candleAccTradeVolume": 12.3,
        "candleAccTradePrice": 1234567.0
      }
    ]
  }
}
```

응답의 `candles`는 `candleDateTimeUtc` 오름차순으로 반환한다. Upbit 원본 응답 순서가 최신순이어도 FastAPI endpoint는 chart가 바로 사용할 수 있는 old-to-new 순서로 정규화한다.

### Upbit unit mapping

| 앱 `CandleUnit` | Upbit endpoint |
| --- | --- |
| `1m` | `/v1/candles/minutes/1` |
| `5m` | `/v1/candles/minutes/5` |
| `15m` | `/v1/candles/minutes/15` |
| `30m` | `/v1/candles/minutes/30` |
| `1h` | `/v1/candles/minutes/60` |
| `1d` | `/v1/candles/days` |
| `1w` | `/v1/candles/weeks` |

Phase 10 문서의 `60m` 표현은 앱 계약의 `1h`로 해석한다. 외부 API와 frontend 계약에는 `1h`만 노출한다.

### 저장 정책

`/api/candles` 응답은 backend state에 저장하지 않는다.

이유:

- 요청 조합이 `market + unit + count + to`로 많다.
- Phase 10 목적은 초기/과거 history 조회다.
- Phase 11의 실시간 마지막 candle 갱신은 WebSocket 경로에서 다룬다.
- ADR-0004는 candle REST response cache를 나중에 필요하면 재검토할 대상으로 둔다.

## Validation

FastAPI/Pydantic은 query parameter의 형식 검증을 담당한다.

추가 domain validation:

- `market`은 기존 `assert_krw_market()` 또는 같은 의미의 검증 함수로 KRW Market만 허용한다.
- `unit`은 `CandleUnit` enum으로 제한한다.
- `count`는 기본 200, 최대 200으로 제한한다.
- `to`는 ISO datetime으로 파싱한다.

실제 Upbit 상장 Market 존재 여부는 `/api/candles` 호출 시 Upbit 응답 결과와 error mapping으로 처리한다. 별도 Market 목록 cache 조회를 candle validation의 필수 선행조건으로 두지 않는다.

## Error Handling

기존 `DashboardApiError`와 error envelope 구조를 확장해서 사용한다.

```json
{
  "type": "error",
  "timestamp": "2026-06-01T00:00:00Z",
  "data": {
    "code": "RATE_LIMITED",
    "message": "Upbit request rate limit exceeded.",
    "details": {
      "upbitStatus": 429,
      "rateLimitGroup": "candle",
      "remainingSec": 0
    }
  }
}
```

Mapping 정책:

| 상황 | 앱 error code | HTTP status |
| --- | --- | --- |
| Query validation 실패 | `VALIDATION_ERROR` | 422 |
| 지원하지 않는 Market 형식 | `VALIDATION_ERROR` | 422 |
| KRW Market이 아님 | `BAD_REQUEST` | 400 |
| Upbit 400 | `UPBIT_BAD_REQUEST` | 502 |
| Upbit 418 | `TEMPORARILY_BLOCKED` | 418 |
| Upbit 429 | `RATE_LIMITED` | 429 |
| Upbit 5xx | `UPBIT_ERROR` | 502 |
| Upbit timeout | `UPBIT_TIMEOUT` | 504 |
| network error | `UPBIT_ERROR` | 502 |

FastAPI의 `RequestValidationError`도 browser-facing route에서는 기존 Message envelope error 형식으로 변환한다.

`/api/markets`에서 Upbit refresh가 실패했지만 stale cache가 있으면 error envelope 대신 성공 `markets:list` 응답을 반환한다.

## Next.js BFF

Next.js에는 다음 Route Handler를 추가한다.

```text
apps/web/src/app/api/markets/route.ts
apps/web/src/app/api/candles/route.ts
```

정책:

- 기존 `fetchBackendJson()`과 `toNextResponse()`를 사용한다.
- BFF에서 별도 cache/revalidation을 설정하지 않는다.
- `/api/candles`는 incoming request의 search params를 FastAPI에 그대로 전달한다.
- BFF는 route-specific Upbit error handling을 직접 구현하지 않는다.

## Frontend 사용 흐름

Frontend 구현은 이 spec의 범위 밖이지만 API 호출 시점은 다음 흐름을 기준으로 한다.

```text
앱 진입
  -> GET /api/markets
  -> GET /api/snapshot
  -> WebSocket ticker:update 수신
```

```text
Selected Market 결정 또는 Candle Unit 변경
  -> GET /api/candles?market=...&unit=...
```

```text
차트 왼쪽 스크롤
  -> 현재 보유한 가장 오래된 candleDateTimeUtc를 to로 전달
  -> GET /api/candles?...&to=...
```

Frontend는 `/api/markets` 결과를 영구 cache 원천으로 관리할 필요는 없지만, Market List 렌더링, 검색, 선택 Market 표시를 위해 client state 또는 query state에는 보관한다.

## Testing

Backend tests:

- `/api/markets`가 Upbit market 목록에서 KRW Market만 반환한다.
- `/api/markets`가 `MarketSummary` camelCase alias로 직렬화된다.
- `/api/markets` fresh cache hit 시 Upbit을 다시 호출하지 않는다.
- `/api/markets` TTL 만료 후 refresh한다.
- `/api/markets` refresh 실패 시 stale cache가 있으면 stale `markets:list`를 반환한다.
- `/api/markets` refresh 실패 시 stale cache가 없으면 error envelope를 반환한다.
- `/api/candles`가 `count` 기본값 200을 적용한다.
- `/api/candles`가 `count > 200`을 거부한다.
- `/api/candles`가 `1h`를 Upbit `/minutes/60`으로 매핑한다.
- `/api/candles`가 `to` query를 Upbit 요청에 전달한다.
- `/api/candles`가 Upbit candle 응답을 `Candle` 계약으로 변환한다.
- `/api/candles`가 candle 목록을 `candleDateTimeUtc` 오름차순으로 반환한다.
- Upbit 418, 429, timeout, network error가 error envelope로 매핑된다.
- FastAPI request validation error가 error envelope로 반환된다.

Frontend/BFF tests:

- `GET /api/markets` Route Handler가 FastAPI `/api/markets`를 호출한다.
- `GET /api/candles` Route Handler가 search params를 보존해 FastAPI `/api/candles`를 호출한다.
- FastAPI upstream error envelope가 BFF에서 그대로 전달된다.

## 완료 기준

- FastAPI `GET /api/markets`가 KRW Market 메타데이터 목록을 반환한다.
- FastAPI `/api/markets`가 10분 cache와 stale-on-error 정책을 따른다.
- Next.js `GET /api/markets` BFF가 FastAPI endpoint를 호출한다.
- FastAPI `GET /api/candles`가 지원 `CandleUnit` 전체를 Upbit REST endpoint로 매핑한다.
- FastAPI `/api/candles`가 기본 200개, 최대 200개 정책을 따른다.
- FastAPI `/api/candles`가 `to` 기반 과거 pagination을 지원한다.
- FastAPI `/api/candles`가 candle 목록을 오름차순으로 반환한다.
- Next.js `GET /api/candles` BFF가 query string을 보존해 FastAPI endpoint를 호출한다.
- Backend와 BFF 테스트가 통과한다.
