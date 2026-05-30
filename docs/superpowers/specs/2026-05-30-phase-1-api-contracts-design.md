# Phase 1 API 이벤트 계약 설계

작성일: 2026-05-30

## 목적

Phase 1의 목적은 실제 Upbit 연결 전에 프론트엔드와 백엔드가 주고받을 데이터 계약을 코드와 문서로 고정하는 것이다.

Phase 1이 끝나면 백엔드는 어떤 JSON을 보낼지 Pydantic 모델로 표현하고, 프론트엔드는 같은 구조를 TypeScript 타입으로 받을 수 있어야 한다. 실제 Upbit WebSocket 연결, 재연결, 메모리 상태 저장, BFF 라우트 구현은 이후 Phase에서 처리한다.

## 근거 문서

- `CONTEXT.md`: Market, Selected Market, MarketState, Snapshot, BFF, Event envelope 용어.
- `docs/adr/0002-bff-upstream-error-handling.md`: BFF upstream 에러 처리는 공통화한다.
- `docs/adr/0003-rest-bff-and-direct-websocket.md`: REST는 Next.js BFF, WebSocket은 FastAPI 직접 연결.
- `docs/adr/0004-process-memory-for-mvp-state.md`: MVP 상태는 FastAPI 프로세스 메모리에 저장.
- `docs/adr/0005-quotation-only-mvp-boundary.md`: MVP는 공개 Quotation data만 사용.
- `docs/upbit/api/quotation/trading-pairs.md`: Market 목록 REST API.
- `docs/upbit/api/quotation/candles.md`: REST candle 단위와 요청 파라미터.
- `docs/upbit/api/websocket/ticker.md`: ticker WebSocket 원본 필드.
- `docs/upbit/api/websocket/trade.md`: trade WebSocket 원본 필드.
- `docs/upbit/api/websocket/orderbook.md`: orderbook WebSocket 원본 필드.
- `docs/upbit/api/websocket/candle.md`: candle WebSocket 원본 필드와 지원 단위.
- `docs/upbit/api/rate-limits.md`: 429, 418, Remaining-Req, WebSocket 요청 제한.
- `docs/upbit/api/rest-api-guide.md`: REST 상태 코드와 Upbit error 응답 형식.
- `docs/upbit/api/websocket-guide.md`: Upbit WebSocket 요청/에러 형식.

## 범위

### 포함

- 백엔드 Pydantic 계약 모델 정의.
- 프론트엔드 TypeScript 계약 타입 정의.
- Upbit WebSocket ticker 원본 모델 정의.
- Upbit ticker 원본 모델을 앱 ticker 계약으로 변환하는 mapper 정의.
- REST 성공/에러 응답 envelope 정의.
- Backend -> Frontend WebSocket 이벤트 envelope 정의.
- 대표 예시 JSON 작성.
- 계약 직렬화, validation, mapper 테스트 작성.

### 제외

- 실제 Upbit WebSocket 연결.
- reconnect/backoff 구현.
- FastAPI `MarketState` 저장소 구현.
- 실제 `/api/snapshot`, `/api/markets`, `/api/candles` endpoint 구현.
- Next.js BFF Route Handler 구현.
- 프론트 UI 구현.
- trade/orderbook/candle Upbit raw 모델 구현.
- 클라이언트 -> 서버 WebSocket command의 세부 lifecycle 구현.

## 기본 정책

### 계약 기준

백엔드 Pydantic 모델을 기준 계약으로 둔다. 프론트 TypeScript 타입은 Pydantic 모델의 JSON 출력 구조에 맞춰 수동 작성한다.

### 필드명

- Python 내부 필드명은 `snake_case`를 사용한다.
- JSON 출력과 TypeScript 타입은 `camelCase`를 사용한다.
- Phase 1에서는 공통 base model을 만들지 않고, 각 Pydantic 모델 필드에 `Field(serialization_alias=..., description=...)`를 직접 명시한다.
- `description`에는 필드 의미와 Upbit 원본 필드명이 있으면 같이 적는다.

예:

```python
trade_price: float = Field(
    serialization_alias="tradePrice",
    description="현재가. Upbit ticker.trade_price 기준.",
)
```

### 숫자 타입

MVP는 주문/정산 시스템이 아니라 Quotation data 표시와 모니터링 시스템이다. Phase 1 계약에서는 가격, 수량, 거래대금, 등락률을 JSON/TypeScript `number`로 둔다. 백엔드 Pydantic 모델은 `float`와 `int` 중심으로 정의하고, `Decimal`은 Phase 1 기본 정책으로 강제하지 않는다.

### timestamp

- Envelope의 `timestamp`는 우리 서버가 응답 또는 이벤트를 만든 시각이다.
- Upbit 원본 ms timestamp는 data 내부에 `timestampMs`, `tradeTimestampMs`처럼 보존한다.
- 모든 ISO timestamp 문자열은 timezone 정보를 포함한다.

## Envelope

### REST 성공 응답

REST 성공 응답은 모두 같은 envelope를 사용한다.

```json
{
  "type": "markets:snapshot",
  "timestamp": "2026-05-30T12:00:00+09:00",
  "data": {}
}
```

REST 성공 `type`:

| Route | type | 의미 |
| --- | --- | --- |
| `GET /api/markets` | `markets:snapshot` | Market 메타데이터 목록 |
| `GET /api/snapshot` | `market-state:snapshot` | 백엔드 MarketState 최신 Snapshot |
| `GET /api/candles` | `candles:snapshot` | 특정 Market과 CandleUnit의 candle 목록 |

### WebSocket 서버 이벤트

Backend -> Frontend WebSocket 이벤트는 브라우저당 FastAPI WebSocket 연결 1개에서 `type`으로 구분한다.

```json
{
  "type": "ticker:update",
  "timestamp": "2026-05-30T12:00:00+09:00",
  "data": {}
}
```

서버 이벤트 `type`:

| type | 의미 |
| --- | --- |
| `ticker:update` | Market ticker 갱신 |
| `trade:update` | Selected Market 체결 갱신 |
| `orderbook:update` | Selected Market 호가 갱신 |
| `candle:update` | Selected Market candle 갱신 |
| `alert:new` | 새 Alert event 생성 |
| `error` | WebSocket 처리 중 오류 |

### WebSocket 클라이언트 command

클라이언트 -> 서버 command도 같은 WebSocket 연결을 사용한다. Phase 1에서는 이름만 예약하고, 세부 lifecycle은 Phase 9에서 정한다.

예약 command:

- `select-market`
- `change-candle-unit`

## 공통 enum

### StreamType

Upbit WebSocket의 `stream_type`을 앱 계약에 보존한다.

```text
SNAPSHOT | REALTIME
```

### AskBid

Upbit WebSocket의 `ask_bid`를 앱 계약에 보존한다.

```text
ASK | BID
```

### CandleUnit

REST `/api/candles`에서 지원하는 앱 candle 단위다.

```text
1m | 5m | 15m | 30m | 1h | 1d | 1w
```

Upbit REST 대응:

| CandleUnit | Upbit REST |
| --- | --- |
| `1m` | `/v1/candles/minutes/1` |
| `5m` | `/v1/candles/minutes/5` |
| `15m` | `/v1/candles/minutes/15` |
| `30m` | `/v1/candles/minutes/30` |
| `1h` | `/v1/candles/minutes/60` |
| `1d` | `/v1/candles/days` |
| `1w` | `/v1/candles/weeks` |

### RealtimeCandleUnit

WebSocket `candle:update`에서 지원하는 앱 candle 단위다.

```text
1m | 5m | 15m | 30m | 1h
```

Upbit WebSocket `candle.{unit}` 문서에는 `1d`, `1w` 실시간 candle 타입이 없다. 따라서 `1d`, `1w` 차트는 REST candle 조회로 커버하고, 실시간 candle update 대상에서 제외한다.

## WebSocket 이벤트 계약

### ticker:update

근거: `docs/upbit/api/websocket/ticker.md`

`ticker:update.data`는 Market List와 Selected Market 헤더에 필요한 공통 ticker 값을 담는다.

| JSON 필드 | 타입 | Upbit 원본 | 설명 |
| --- | --- | --- | --- |
| `market` | string | `code` | Market 코드. 예: `KRW-BTC` |
| `openingPrice` | number | `opening_price` | 시가 |
| `highPrice` | number | `high_price` | 고가 |
| `lowPrice` | number | `low_price` | 저가 |
| `tradePrice` | number | `trade_price` | 현재가 |
| `signedChangePrice` | number | `signed_change_price` | 전일 대비 가격 변동 값 |
| `signedChangeRate` | number | `signed_change_rate` | 전일 대비 등락률 |
| `tradeVolume` | number | `trade_volume` | 최근 거래량 |
| `accTradeVolume24h` | number | `acc_trade_volume_24h` | 최근 24시간 누적 거래량 |
| `accTradePrice24h` | number | `acc_trade_price_24h` | 최근 24시간 누적 거래대금 |
| `tradeTimestampMs` | number | `trade_timestamp` | 체결 타임스탬프(ms) |
| `timestampMs` | number | `timestamp` | Upbit 이벤트 타임스탬프(ms) |
| `streamType` | `StreamType` | `stream_type` | `SNAPSHOT` 또는 `REALTIME` |

예:

```json
{
  "type": "ticker:update",
  "timestamp": "2026-05-30T12:00:00+09:00",
  "data": {
    "market": "KRW-BTC",
    "openingPrice": 108000000,
    "highPrice": 109000000,
    "lowPrice": 107500000,
    "tradePrice": 108359000,
    "signedChangePrice": -106000,
    "signedChangeRate": -0.001,
    "tradeVolume": 0.01,
    "accTradeVolume24h": 1288.5,
    "accTradePrice24h": 139663338391,
    "tradeTimestampMs": 1760000000000,
    "timestampMs": 1760000000100,
    "streamType": "REALTIME"
  }
}
```

### trade:update

근거: `docs/upbit/api/websocket/trade.md`

`trade:update.data`는 최근 체결 UI와 중복 처리를 위한 최소 체결 정보를 담는다.

| JSON 필드 | 타입 | Upbit 원본 | 설명 |
| --- | --- | --- | --- |
| `market` | string | `code` | Market 코드 |
| `tradePrice` | number | `trade_price` | 체결 가격 |
| `tradeVolume` | number | `trade_volume` | 체결량 |
| `askBid` | `AskBid` | `ask_bid` | 매수/매도 구분 |
| `tradeTimestampMs` | number | `trade_timestamp` | 체결 타임스탬프(ms) |
| `sequentialId` | number | `sequential_id` | 체결 번호. 중복/순서 처리에 사용 |
| `timestampMs` | number | `timestamp` | Upbit 이벤트 타임스탬프(ms) |
| `streamType` | `StreamType` | `stream_type` | `SNAPSHOT` 또는 `REALTIME` |

제외 필드:

- `prev_closing_price`, `change`, `change_price`: ticker 역할과 중복된다.
- `best_ask_price`, `best_ask_size`, `best_bid_price`, `best_bid_size`: orderbook 역할과 중복된다.

예:

```json
{
  "type": "trade:update",
  "timestamp": "2026-05-30T12:00:00+09:00",
  "data": {
    "market": "KRW-BTC",
    "tradePrice": 108359000,
    "tradeVolume": 0.01,
    "askBid": "BID",
    "tradeTimestampMs": 1760000000000,
    "sequentialId": 123456789,
    "timestampMs": 1760000000100,
    "streamType": "REALTIME"
  }
}
```

### orderbook:update

근거: `docs/upbit/api/websocket/orderbook.md`

`orderbook:update.data`는 호가창 UI에 필요한 가격/잔량 목록과 총 잔량을 담는다.

| JSON 필드 | 타입 | Upbit 원본 | 설명 |
| --- | --- | --- | --- |
| `market` | string | `code` | Market 코드 |
| `totalAskSize` | number | `total_ask_size` | 매도 총 잔량 |
| `totalBidSize` | number | `total_bid_size` | 매수 총 잔량 |
| `level` | number | `level` | 호가 모아보기 단위 |
| `units` | `OrderbookUnit[]` | `orderbook_units` | 호가 목록 |
| `timestampMs` | number | `timestamp` | Upbit 이벤트 타임스탬프(ms) |
| `streamType` | `StreamType` | `stream_type` | `SNAPSHOT` 또는 `REALTIME` |

`OrderbookUnit`:

| JSON 필드 | 타입 | Upbit 원본 | 설명 |
| --- | --- | --- | --- |
| `askPrice` | number | `orderbook_units.ask_price` | 매도 호가 |
| `bidPrice` | number | `orderbook_units.bid_price` | 매수 호가 |
| `askSize` | number | `orderbook_units.ask_size` | 매도 잔량 |
| `bidSize` | number | `orderbook_units.bid_size` | 매수 잔량 |

정책:

- `units` 순서는 Upbit `orderbook_units` 순서를 유지한다.
- Phase 1 계약은 `level=0`을 기본으로 둔다.
- `{pair_code}.{unit}`을 통한 호가 개수 1, 5, 15, 30 선택은 Phase 9 구독 관리에서 확정한다.

예:

```json
{
  "type": "orderbook:update",
  "timestamp": "2026-05-30T12:00:00+09:00",
  "data": {
    "market": "KRW-BTC",
    "totalAskSize": 12.34,
    "totalBidSize": 10.12,
    "level": 0,
    "units": [
      {
        "askPrice": 108400000,
        "bidPrice": 108300000,
        "askSize": 0.5,
        "bidSize": 0.7
      }
    ],
    "timestampMs": 1760000000100,
    "streamType": "REALTIME"
  }
}
```

### candle:update

근거:

- `docs/upbit/api/quotation/candles.md`
- `docs/upbit/api/websocket/candle.md`

`candle:update`는 `RealtimeCandleUnit`만 대상으로 한다.

`Candle`:

| JSON 필드 | 타입 | Upbit 원본 | 설명 |
| --- | --- | --- | --- |
| `candleDateTimeUtc` | string | `candle_date_time_utc` | 캔들 기준 시각 UTC |
| `candleDateTimeKst` | string | `candle_date_time_kst` | 캔들 기준 시각 KST |
| `openingPrice` | number | `opening_price` | 시가 |
| `highPrice` | number | `high_price` | 고가 |
| `lowPrice` | number | `low_price` | 저가 |
| `tradePrice` | number | `trade_price` | 종가 |
| `candleAccTradeVolume` | number | `candle_acc_trade_volume` | 누적 거래량 |
| `candleAccTradePrice` | number | `candle_acc_trade_price` | 누적 거래금액 |

`candle:update.data`:

| JSON 필드 | 타입 | 설명 |
| --- | --- | --- |
| `market` | string | Market 코드 |
| `candleUnit` | `RealtimeCandleUnit` | 실시간 candle 단위 |
| `candle` | `Candle` | OHLCV candle 값 |
| `timestampMs` | number | Upbit candle WebSocket `timestamp` |
| `streamType` | `StreamType` | `SNAPSHOT` 또는 `REALTIME` |

정책:

- candle key는 `market + candleUnit + candle.candleDateTimeUtc` 조합이다.
- 같은 candle key가 다시 오면 마지막 수신 값을 최신으로 본다.
- WebSocket candle은 체결이 없으면 전송되지 않을 수 있다.
- `1d`, `1w`는 WebSocket 실시간 업데이트 대상이 아니다.

예:

```json
{
  "type": "candle:update",
  "timestamp": "2026-05-30T12:00:01+09:00",
  "data": {
    "market": "KRW-BTC",
    "candleUnit": "1m",
    "candle": {
      "candleDateTimeUtc": "2026-05-30T03:00:00Z",
      "candleDateTimeKst": "2026-05-30T12:00:00+09:00",
      "openingPrice": 108000000,
      "highPrice": 109000000,
      "lowPrice": 107500000,
      "tradePrice": 108359000,
      "candleAccTradeVolume": 12.34,
      "candleAccTradePrice": 139663338391
    },
    "timestampMs": 1760000000100,
    "streamType": "REALTIME"
  }
}
```

### alert:new

`alert:new`은 Upbit 원본 이벤트가 아니라 백엔드가 Quotation data로 계산해 만드는 앱 이벤트다.

MVP alert 종류:

```text
dailyRise | dailyDrop | shortTermRise | shortTermDrop
```

필드:

| JSON 필드 | 타입 | 설명 |
| --- | --- | --- |
| `id` | string | 프론트 리스트 key와 중복 방지용 ID |
| `market` | string | Alert 대상 Market |
| `alertKind` | `AlertKind` | Alert 종류 |
| `title` | string | UI에 표시할 짧은 제목 |
| `message` | string | UI에 표시할 메시지 |
| `severity` | `info | warning` | 표시 심각도 |
| `basisRate` | number | Alert를 발생시킨 등락률 |
| `basisWindow` | `24h | 1m` | Alert 계산 기준 구간 |
| `createdAt` | string | Alert 생성 시각 |

예:

```json
{
  "type": "alert:new",
  "timestamp": "2026-05-30T12:00:00+09:00",
  "data": {
    "id": "20260530T120000-KRW-BTC-daily-rise",
    "market": "KRW-BTC",
    "alertKind": "dailyRise",
    "title": "KRW-BTC 전일 대비 급등",
    "message": "전일 대비 +5.2%",
    "severity": "info",
    "basisRate": 0.052,
    "basisWindow": "24h",
    "createdAt": "2026-05-30T12:00:00+09:00"
  }
}
```

Phase 1은 alert 이벤트 계약만 정의한다. 실제 alert 계산은 short-term price history가 생기는 이후 Phase에서 구현한다.

## REST 계약

### GET /api/markets

역할: Market 검색과 표시용 메타데이터를 반환한다. 현재가 정보는 포함하지 않는다.

응답:

```json
{
  "type": "markets:snapshot",
  "timestamp": "2026-05-30T12:00:00+09:00",
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

`MarketSummary`:

| JSON 필드 | 타입 | 설명 |
| --- | --- | --- |
| `market` | string | Upbit Market 코드 |
| `koreanName` | string | 한글 Market 이름 |
| `englishName` | string | 영문 Market 이름 |
| `quoteCurrency` | string | 기준 통화. 예: `KRW` |
| `baseCurrency` | string | 대상 자산. 예: `BTC` |

### GET /api/snapshot

역할: 백엔드 `MarketState`가 가진 최신 ticker snapshot을 초기 화면용으로 반환한다.

응답:

```json
{
  "type": "market-state:snapshot",
  "timestamp": "2026-05-30T12:00:00+09:00",
  "data": {
    "generatedAt": "2026-05-30T12:00:00+09:00",
    "tickers": [
      {
        "market": "KRW-BTC",
        "openingPrice": 108000000,
        "highPrice": 109000000,
        "lowPrice": 107500000,
        "tradePrice": 108359000,
        "signedChangePrice": -106000,
        "signedChangeRate": -0.001,
        "tradeVolume": 0.01,
        "accTradeVolume24h": 1288.5,
        "accTradePrice24h": 139663338391,
        "tradeTimestampMs": 1760000000000,
        "timestampMs": 1760000000100,
        "streamType": "REALTIME"
      }
    ]
  }
}
```

정책:

- `tickers[]`의 원소는 `ticker:update.data`와 같은 `TickerData` 구조를 사용한다.
- Phase 2에서는 `KRW-BTC`, `KRW-ETH`처럼 제한된 Market만 들어갈 수 있다.
- Phase 8 이후에는 전체 KRW Market으로 확장된다.

### GET /api/candles

역할: 선택 Market의 초기/과거 candle 데이터를 반환한다.

요청 query:

| Query | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `market` | string | 필수 | Market 코드 |
| `candleUnit` | `CandleUnit` | 필수 | 앱 candle 단위 |
| `count` | integer | 선택 | 조회 개수 |
| `to` | string | 선택 | 조회 기준 시각 |

응답:

```json
{
  "type": "candles:snapshot",
  "timestamp": "2026-05-30T12:00:00+09:00",
  "data": {
    "market": "KRW-BTC",
    "candleUnit": "1m",
    "candles": [
      {
        "candleDateTimeUtc": "2026-05-30T03:00:00Z",
        "candleDateTimeKst": "2026-05-30T12:00:00+09:00",
        "openingPrice": 108000000,
        "highPrice": 109000000,
        "lowPrice": 107500000,
        "tradePrice": 108359000,
        "candleAccTradeVolume": 12.34,
        "candleAccTradePrice": 139663338391
      }
    ]
  }
}
```

정책:

- `data.candles[]`는 `candleDateTimeUtc` 오름차순으로 반환한다.
- Upbit REST 원본 응답 순서와 상관없이 앱 REST 계약에서 정렬을 보장한다.
- 체결이 없는 구간은 candle이 없을 수 있다. 프론트는 시간축이 항상 연속된다고 가정하지 않는다.
- `data.market`, `data.candleUnit`이 상위에 있으므로 개별 `Candle`에는 중복해서 넣지 않는다.

## Upbit raw 모델

Phase 1에서는 Phase 2에서 바로 사용할 `UpbitTickerMessage`만 raw Pydantic 모델로 정의한다.

`UpbitTickerMessage` 필드:

| Python 필드 | Upbit 원본 | 설명 |
| --- | --- | --- |
| `type` | `type` | 원본 데이터 항목. `ticker` |
| `code` | `code` | Market 코드 |
| `opening_price` | `opening_price` | 시가 |
| `high_price` | `high_price` | 고가 |
| `low_price` | `low_price` | 저가 |
| `trade_price` | `trade_price` | 현재가 |
| `signed_change_price` | `signed_change_price` | 전일 대비 가격 변동 값 |
| `signed_change_rate` | `signed_change_rate` | 전일 대비 등락률 |
| `trade_volume` | `trade_volume` | 최근 거래량 |
| `acc_trade_volume_24h` | `acc_trade_volume_24h` | 최근 24시간 누적 거래량 |
| `acc_trade_price_24h` | `acc_trade_price_24h` | 최근 24시간 누적 거래대금 |
| `trade_timestamp` | `trade_timestamp` | 체결 타임스탬프(ms) |
| `timestamp` | `timestamp` | 이벤트 타임스탬프(ms) |
| `stream_type` | `stream_type` | `SNAPSHOT` 또는 `REALTIME` |

Phase 1 mapper:

```text
UpbitTickerMessage.code -> TickerData.market
UpbitTickerMessage.trade_price -> TickerData.trade_price
UpbitTickerMessage.timestamp -> TickerData.timestamp_ms
```

trade/orderbook/candle raw 모델은 실제 구독 구현 Phase에서 문서와 샘플을 기준으로 정의한다.

## 에러 계약

REST와 WebSocket 에러 모두 envelope를 사용한다.

```json
{
  "type": "error",
  "timestamp": "2026-05-30T12:00:00+09:00",
  "data": {
    "code": "RATE_LIMITED",
    "message": "Upbit request rate limit exceeded.",
    "details": {
      "upbitStatus": 429,
      "rateLimitGroup": "candle",
      "remainingSec": 0,
      "upbitErrorName": "too_many_requests"
    }
  }
}
```

### REST 상태 코드 매핑

| HTTP status | code | 의미 |
| --- | --- | --- |
| 400 | `BAD_REQUEST` | 요청 형식은 맞지만 의미가 잘못됨. 예: 해당 context에서 허용되지 않는 `candleUnit`, `count` 정책 범위 초과 |
| 404 | `NOT_FOUND` | 앱 리소스 없음. 예: 알 수 없는 Market |
| 418 | `TEMPORARILY_BLOCKED` | Upbit 과다 요청으로 일시 차단 |
| 422 | `VALIDATION_ERROR` | 스키마 검증 실패. 예: 필수 query 누락, 타입 불일치, enum에 없는 `candleUnit` |
| 429 | `RATE_LIMITED` | Upbit 요청 제한 초과 |
| 502 | `UPBIT_BAD_REQUEST` | 우리 검증은 통과했지만 Upbit이 400 계열 오류를 반환 |
| 502 | `UPBIT_ERROR` | 그 외 Upbit upstream 오류 |
| 504 | `UPBIT_TIMEOUT` | Upbit 응답 timeout |
| 500 | `INTERNAL_ERROR` | 우리 서버 내부 오류 |

정책:

- `VALIDATION_ERROR`는 우리 API 스키마 검증 실패에만 사용한다.
- `BAD_REQUEST`는 스키마는 맞지만 값의 의미가 잘못된 경우에 사용한다.
- Upbit 원본 error 응답은 `details.upbitErrorName`, `details.upbitErrorMessage`, `details.upbitStatus`에 보존한다.
- Upbit `Remaining-Req` 헤더에서 확인한 값은 가능하면 `details.rateLimitGroup`, `details.remainingSec`에 보존한다.
- 418 차단 시간이 응답에 포함되면 `details.retryAfterSeconds` 또는 `details.blockedUntil`에 보존한다.

### WebSocket 에러 코드

WebSocket에는 HTTP status가 없으므로 `type: "error"`와 `data.code`로 표현한다.

| code | 의미 |
| --- | --- |
| `INVALID_MESSAGE` | 메시지가 JSON object가 아니거나 envelope 구조가 아님 |
| `UNSUPPORTED_MESSAGE_TYPE` | 지원하지 않는 client command type |
| `INVALID_MARKET` | 지원하지 않는 Market |
| `BAD_REQUEST` | 메시지 의미가 잘못됨 |
| `VALIDATION_ERROR` | 메시지 스키마 검증 실패 |
| `RATE_LIMITED` | Upbit 또는 앱 WebSocket 요청 제한 초과 |
| `TEMPORARILY_BLOCKED` | Upbit 일시 차단 |
| `UPBIT_WS_ERROR` | Upbit WebSocket error 응답 |
| `INTERNAL_ERROR` | 우리 서버 내부 오류 |

Upbit WebSocket 원본 에러 `INVALID_AUTH`, `WRONG_FORMAT`, `NO_TICKET`, `NO_TYPE`, `NO_CODES`, `INVALID_PARAM`은 앱 `UPBIT_WS_ERROR`의 details에 보존한다. Public Quotation WebSocket만 사용하는 MVP에서는 인증 관련 에러가 정상 흐름에 나오지 않아야 한다.

## 파일 계획

### Backend

```text
apps/backend/src/upbit_dashboard/contracts/__init__.py
apps/backend/src/upbit_dashboard/contracts/events.py
apps/backend/src/upbit_dashboard/contracts/rest.py
apps/backend/src/upbit_dashboard/contracts/upbit.py
apps/backend/src/upbit_dashboard/contracts/mappers.py
apps/backend/src/upbit_dashboard/contracts/errors.py
```

역할:

- `events.py`: WebSocket event envelope와 event data 모델.
- `rest.py`: REST success envelope와 REST data 모델.
- `upbit.py`: Phase 1에서 필요한 Upbit raw 모델. 우선 `UpbitTickerMessage`.
- `mappers.py`: raw Upbit 모델을 앱 계약 모델로 변환.
- `errors.py`: error envelope, error code enum, REST status 매핑.

### Frontend

```text
apps/web/src/lib/contracts/events.ts
apps/web/src/lib/contracts/rest.ts
apps/web/src/lib/contracts/errors.ts
```

역할:

- `events.ts`: Backend -> Frontend WebSocket event union.
- `rest.ts`: REST response 타입.
- `errors.ts`: Error response 타입과 error code union.

## 테스트 계획

### Backend tests

```text
apps/backend/tests/test_contract_serialization.py
apps/backend/tests/test_upbit_ticker_mapper.py
apps/backend/tests/test_error_contracts.py
```

검증:

- Pydantic 모델이 `serialization_alias` 기준 camelCase JSON을 출력한다.
- 각 필드 description이 JSON schema에 포함된다.
- 필수 필드 누락과 enum 오류가 validation error로 잡힌다.
- `UpbitTickerMessage -> TickerData` 변환이 정확하다.
- REST error status와 `data.code` 매핑이 정확하다.
- `400 BAD_REQUEST`와 `422 VALIDATION_ERROR`가 분리된다.
- `429 RATE_LIMITED`와 `418 TEMPORARILY_BLOCKED`가 분리된다.

### Frontend checks

Phase 1에서는 프론트 타입 파일을 작성하고 TypeScript compile 대상에 포함한다. 별도 프론트 테스트 러너가 없으면 `pnpm -C apps/web lint` 또는 build/typecheck 가능한 명령으로 타입 오류가 없는지 확인한다.

## 구현 순서

1. 백엔드 `contracts` 패키지를 만든다.
2. 공통 enum과 error 모델을 작성한다.
3. WebSocket event data Pydantic 모델을 작성한다.
4. REST response Pydantic 모델을 작성한다.
5. `UpbitTickerMessage` raw 모델을 작성한다.
6. `UpbitTickerMessage -> TickerData` mapper를 작성한다.
7. 백엔드 계약 테스트를 작성한다.
8. 프론트 TypeScript 계약 타입을 작성한다.
9. 타입/테스트 검증 명령을 실행한다.
10. `docs/development-sequence.md`의 Phase 1 설명을 이 스펙 기준으로 요약 갱신한다.

## 완료 기준

- Phase 1 계약 모델이 백엔드 Pydantic 코드로 존재한다.
- Phase 1 계약 타입이 프론트 TypeScript 코드로 존재한다.
- 대표 REST/WebSocket payload가 이 문서와 코드에서 같은 구조를 가진다.
- 백엔드 테스트가 Pydantic alias, description, validation, mapper, error mapping을 검증한다.
- 프론트 타입이 TypeScript 검증을 통과한다.
- 실제 Upbit 연결 없이도 Phase 2에서 ticker 수신 결과를 `TickerData`로 변환할 준비가 끝난다.
