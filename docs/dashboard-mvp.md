# 업비트 실시간 모니터링 대시보드 MVP

정리일: 2026-05-29

## 목표

업비트 공개 시세 API를 이용해 로그인 없이 사용할 수 있는 실시간 모니터링 대시보드를 만든다. 초기 목표는 매매 실행이 아니라 전체 KRW 마켓의 빠른 시세 변화 확인, 선택 종목 상세 확인, 간단한 시장 변화 알림이다.

## 제외 범위

- 실제 매수/매도 주문 실행
- 업비트 API Key 인증
- 로그인/회원 기능
- 개인 관심종목 저장
- 개인화 알림 설정
- 모의투자 체결/포트폴리오 저장

주문 폼 UI는 배치할 수 있지만 MVP에서는 기능을 비활성화한다.

## 화면 레이아웃

업비트 거래 화면과 유사한 구성을 따른다.

```text
┌──────────────────────────────────────────────┬──────────────────────┐
│ 선택 종목 헤더 + 요약                         │ 검색 / 마켓 탭        │
│ 현재가, 전일대비, 고가, 저가, 거래량, 거래대금  │ [KRW] [BTC] [USDT]   │
├──────────────────────────────────────────────┤ 전체 종목 리스트      │
│ 차트                                          │ 종목 / 현재가 / 등락률 │
│ 1m 5m 15m 30m 1h 1d 1w                       │ 거래대금              │
├──────────────────────┬───────────────────────┤                      │
│ 호가창                │ 주문 폼 UI             │                      │
│                      │ 기능 없음 / 준비중      │                      │
├──────────────────────┴───────────────────────┤                      │
│ 최근 체결 / 알림 피드                         │                      │
└──────────────────────────────────────────────┴──────────────────────┘
```

오른쪽 전체 종목 리스트는 고정한다. 중앙/왼쪽 영역은 선택 종목 상세를 보여준다.

## MVP 기능

### 전체 KRW 종목 리스트

- KRW 마켓 전체 종목 표시
- 현재가
- 전일 대비 가격
- 전일 대비 등락률
- 24시간 거래대금
- 기본 정렬: 24시간 거래대금 내림차순
- 종목명/심볼 검색

거래량은 테이블 컬럼에서 제외하고 차트 내부 거래량 막대로 표시한다.

### 선택 종목 상세

- 선택 종목명과 심볼
- 현재가
- 전일 대비 가격과 등락률
- 고가
- 저가
- 거래량
- 거래대금
- 캔들 차트
- 호가창
- 최근 체결 내역
- 주문 폼 UI

주문 폼은 디자인만 제공한다. 실제 주문 기능은 없다.

### 차트

지원 시간 단위:

- 1분
- 5분
- 15분
- 30분
- 1시간
- 일봉
- 주봉

제외:

- 1초봉

초기 차트 데이터는 REST 캔들 API로 가져온다. 사용자가 차트를 왼쪽으로 스크롤하면 가장 오래된 캔들 시간을 기준으로 과거 데이터를 추가 조회한다.

차트 내부에는 거래량을 함께 표시한다.

### 호가창

선택 종목 1개의 실시간 호가를 표시한다.

- 매도 호가
- 매도 잔량
- 매수 호가
- 매수 잔량
- 현재가 기준 구분

데이터는 WebSocket `orderbook`을 사용한다.

### 최근 체결 내역

선택 종목 1개의 실시간 체결을 표시한다.

- 체결 시간
- 체결 가격
- 체결량
- 매수/매도 구분

데이터는 WebSocket `trade`를 사용한다.

### 알림 피드

복잡한 설정 없이 전체 시장에서 주목할 만한 변화만 표시한다.

MVP 알림:

- 전일 대비 급등/급락
- 최근 1분 가격 급변

알림 UI 설정, 토글, 임계값 변경 화면은 만들지 않는다. 임계값은 내부 설정값으로 분리한다.

## 데이터 흐름

```text
Upbit WebSocket
      │
      ▼
Backend
  ├─ 전체 KRW ticker 수집
  ├─ 선택 종목 trade 수집
  ├─ 선택 종목 orderbook 수집
  ├─ 선택 종목 candle 수집
  └─ 알림 이벤트 계산
      │
      ▼
App WebSocket
      │
      ▼
Frontend
  ├─ 전체 종목 테이블 업데이트
  ├─ 선택 종목 차트 업데이트
  ├─ 호가창 업데이트
  ├─ 최근 체결 업데이트
  └─ 알림 피드 추가
```

## 통신 방식

### Upbit -> Backend

WebSocket을 사용한다.

항상 수집:

- KRW 전체 `ticker`

선택적으로 수집:

- 선택 종목 `trade`
- 선택 종목 `orderbook`
- 선택 종목 `candle`

전체 시장을 보는 데이터는 넓게 수집하고, 상세 데이터는 사용자가 보고 있는 종목 중심으로 좁게 수집한다.

### Backend -> Frontend

WebSocket을 사용한다.

브라우저는 실시간 데이터 수신을 위해 FastAPI WebSocket endpoint에 직접 연결한다.

서버에서 프론트로 보내는 이벤트 예:

- `ticker:update`
- `market:selected:update`
- `trade:update`
- `orderbook:update`
- `candle:update`
- `alert:new`

프론트에서 서버로 보내는 이벤트 예:

- `select-market`
- `change-candle-unit`
- `subscribe`
- `unsubscribe`

### REST API 역할

REST는 실시간 스트림이 아니라 초기 데이터와 과거 데이터를 가져오는 용도로 사용한다. REST 요청은 브라우저가 FastAPI를 직접 호출하지 않고 Next.js Route Handler를 BFF로 경유한다.

```text
Next Frontend
  -> Next.js Route Handler
  -> FastAPI REST API
```

이 구조에서는 브라우저 기준 REST 요청 대상이 Next.js와 같은 origin이므로 REST CORS 처리를 단순화할 수 있다. 단, WebSocket은 브라우저가 FastAPI에 직접 연결하므로 FastAPI에서 허용 Origin을 관리한다.

예:

- `GET /api/markets`: 전체 페어 목록
- `GET /api/snapshot`: 서버가 가진 최신 ticker 스냅샷
- `GET /api/candles`: 선택 종목 차트 초기 데이터
- `GET /api/candles?to=...`: 차트 좌측 스크롤 시 과거 캔들 추가 조회

## 여러 사용자 구조

여러 사용자가 동시에 접속할 수 있는 구조를 전제로 한다.

- 전체 KRW ticker는 서버가 1번만 구독하고 모든 클라이언트에 공유한다.
- 선택 종목 상세 데이터는 클라이언트들이 보고 있는 종목 집합을 합쳐서 구독한다.
- 같은 종목을 여러 사용자가 선택해도 Upbit에는 중복 구독하지 않는다.
- 수신한 상세 데이터는 해당 종목을 보고 있는 클라이언트에게만 전달한다.

예:

```text
A 사용자: KRW-BTC 선택
B 사용자: KRW-BTC 선택
C 사용자: KRW-ETH 선택

Backend detail subscription:
- KRW-BTC
- KRW-ETH

전송:
- KRW-BTC 상세 데이터 -> A, B
- KRW-ETH 상세 데이터 -> C
```

## 차트 과거 조회 정책

차트 과거 조회는 시간 cursor 기반 pagination으로 처리한다.

```text
최초 요청:
GET /api/candles?market=KRW-BTC&unit=1m&count=200

더 과거 요청:
GET /api/candles?market=KRW-BTC&unit=1m&to=<oldest-candle-time>&count=200
```

조회 제한은 코드에 고정하지 않고 설정값으로 둔다.

예:

```ts
const candleLookbackPolicy = {
  enabled: true,
  limits: {
    "1m": "1d",
    "5m": "3d",
    "15m": "7d",
    "30m": "14d",
    "60m": "30d",
    "1d": "1y",
    "1w": "3y",
  },
};
```

제한을 끌 수 있도록 한다.

```ts
const candleLookbackPolicy = {
  enabled: false,
  limits: {},
};
```

## 알림 정책

알림 기준은 UI 설정 없이 내부 설정값으로 관리한다.

예:

```ts
const alertPolicy = {
  dailyRiseRate: 0.05,
  dailyDropRate: -0.05,
  shortTermWindowMs: 60_000,
  shortTermRiseRate: 0.02,
  shortTermDropRate: -0.02,
};
```

알림 이벤트 예:

```text
[12:04:11] KRW-XRP 전일 대비 +5% 돌파
[12:06:45] KRW-SOL 최근 1분 +2% 급등
```

## Upbit API 사용 계획

REST:

- 페어 목록 조회: `GET /v1/market/all`
- 캔들 조회: `/v1/candles/minutes/{unit}`, `/v1/candles/days`, `/v1/candles/weeks`

WebSocket:

- 전체 종목 현재가: `ticker`
- 선택 종목 체결: `trade`
- 선택 종목 호가: `orderbook`
- 선택 종목 캔들: `candle.{unit}`

인증이 필요한 Exchange API는 MVP에서 사용하지 않는다.

## 확장 후보

- BTC/USDT 마켓 탭 활성화
- 관심종목
- 로그인
- 개인 알림 설정
- 모의투자 주문 체결
- 포트폴리오/손익 계산
- 알림 저장
- 여러 차트 동시 보기
- 호가 불균형 알림
- 거래량 급증 알림
