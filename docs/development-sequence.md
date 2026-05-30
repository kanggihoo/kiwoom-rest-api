# 업비트 대시보드 개발 순서

정리일: 2026-05-30

## 전제

이 문서는 업비트 실시간 모니터링 대시보드 MVP를 어떤 순서로 개발할지 정리한다.

확정된 큰 방향:

- Frontend: Next.js, TypeScript, Tailwind CSS, pnpm
- Backend: FastAPI, Uvicorn, websockets, Pydantic, uv
- DB/Redis: MVP에서는 사용하지 않음
- REST: Next.js Route Handler를 BFF로 사용해 FastAPI REST API를 호출
- WebSocket: Next Frontend가 FastAPI WebSocket endpoint에 직접 연결
- Upbit 인증 API: MVP에서는 사용하지 않음
- 주문 기능: UI만 제공하고 실제 기능 없음

## 전체 전략

실시간 데이터 프로젝트는 화면보다 데이터 파이프라인 리스크가 크다. 따라서 개발 순서는 다음 원칙을 따른다.

1. 작은 Upbit WebSocket 연결부터 검증한다.
2. 백엔드가 최신 상태를 메모리에 보관하게 만든다.
3. 프론트 UI는 먼저 mock 데이터로 만든다.
4. 그 뒤 실제 WebSocket 데이터를 연결한다.
5. 전체 KRW 종목 확장은 마지막에 한다.

## Phase 0. 프로젝트 골격

목표: 프론트와 백엔드를 독립적으로 실행할 수 있는 기본 구조를 만든다.

작업:

- `apps/web`에 Next.js 앱 구성
- `apps/backend`에 FastAPI 앱 구성
- pnpm 기반 프론트 의존성 관리
- uv 기반 백엔드 의존성 관리
- 로컬 실행 명령 정리
- `.env.local`, `.env` 예시 정리

예상 로컬 포트:

```text
Next.js: http://localhost:3000
FastAPI: http://localhost:8000
FastAPI WebSocket: ws://localhost:8000/ws
```

완료 기준:

- Next.js 기본 화면이 열린다.
- FastAPI health endpoint가 응답한다.
- 프론트에서 Next Route Handler를 통해 FastAPI health를 확인할 수 있다.

## Phase 1. API 이벤트 계약 정의

목표: 프론트와 백엔드가 주고받을 REST/WebSocket 메시지 형태를 먼저 고정한다.

작업:

- FastAPI Pydantic 모델 정의
- WebSocket event envelope 정의
- ticker, trade, orderbook, candle, alert 이벤트 타입 정의
- REST 응답 스키마 정의

이벤트 예:

```json
{
  "type": "ticker:update",
  "data": {
    "market": "KRW-BTC",
    "tradePrice": 108359000,
    "signedChangePrice": -106000,
    "signedChangeRate": -0.001,
    "accTradePrice24h": 139663338391
  }
}
```

완료 기준:

- 프론트와 백엔드가 사용할 이벤트 이름이 문서화되어 있다.
- Pydantic 모델 기준으로 REST 응답이 검증된다.
- 프론트 타입은 이 스키마를 기준으로 작성할 수 있다.

## Phase 2. Upbit ticker 최소 연결

목표: FastAPI 백엔드에서 Upbit WebSocket에 연결해 ticker를 실제로 수신한다.

작업:

- `wss://api.upbit.com/websocket/v1` 연결
- `KRW-BTC`, `KRW-ETH`만 ticker 구독
- 수신 메시지 파싱
- reconnect/backoff 기본 처리
- ping/pong 또는 idle timeout 대응 확인

완료 기준:

- 백엔드 로그에서 `KRW-BTC`, `KRW-ETH` ticker가 실시간으로 확인된다.
- Upbit 연결이 끊겨도 재연결을 시도한다.
- 서버 재시작 시 구독 메시지가 다시 전송된다.

## Phase 3. Backend 메모리 상태 저장

목표: 수신한 ticker를 백엔드 프로세스 메모리에 최신 상태로 저장한다.

작업:

- `MarketState` 구성
- `tickers: dict[market, Ticker]` 관리
- 최신 ticker snapshot 조회 함수 추가
- `GET /api/snapshot` FastAPI endpoint 추가

의미:

```text
Upbit ticker 이벤트 수신
  -> MarketState 업데이트
  -> 새 접속자에게 최신 snapshot 제공 가능
```

완료 기준:

- `/api/snapshot`이 현재 백엔드가 보유한 최신 ticker를 반환한다.
- 새 프론트 사용자가 접속해도 빈 화면 대신 최신 snapshot을 받을 수 있다.

## Phase 4. REST BFF 연결

목표: 브라우저가 FastAPI REST를 직접 호출하지 않고 Next.js Route Handler를 통해 호출하게 만든다.

작업:

- Next.js `GET /api/snapshot` Route Handler 추가
- Next.js `GET /api/markets` Route Handler 추가
- Next.js `GET /api/candles` Route Handler 추가
- 내부에서 `FASTAPI_BASE_URL`로 FastAPI 호출

데이터 흐름:

```text
Browser
  -> Next.js /api/snapshot
  -> FastAPI /api/snapshot
```

완료 기준:

- 브라우저 REST 요청 대상은 항상 Next.js origin이다.
- REST CORS 설정 없이 snapshot을 가져올 수 있다.
- FastAPI URL은 브라우저에 노출하지 않는다.

## Phase 5. Frontend 레이아웃 mock

목표: 실제 데이터 연결 전 업비트 스타일 화면 골격을 만든다.

작업:

- 오른쪽 전체 종목 리스트 고정
- 중앙 선택 종목 헤더
- 차트 영역
- 호가창 영역
- 주문 폼 UI 영역
- 최근 체결/알림 피드 영역
- mock ticker 데이터로 테이블 표시

완료 기준:

- 업비트와 유사한 레이아웃이 보인다.
- 오른쪽 종목 리스트가 고정되어 있다.
- 주문 폼은 보이지만 버튼은 비활성화되어 있다.

## Phase 6. Frontend WebSocket 연결

목표: Next Frontend가 FastAPI WebSocket에 직접 연결해 실시간 이벤트를 받는다.

작업:

- 프론트 WebSocket client wrapper 작성
- `NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws` 사용
- 연결 상태 표시
- 재연결 처리
- FastAPI WebSocket origin allowlist 추가
- `ticker:update` 이벤트 수신

완료 기준:

- 프론트가 FastAPI WebSocket에 연결된다.
- 연결 끊김/재연결 상태가 UI에서 보인다.
- `KRW-BTC`, `KRW-ETH` ticker가 화면에 반영된다.

## Phase 7. ticker 배치 반영

목표: ticker 이벤트가 많이 들어와도 React 렌더링이 과도하게 발생하지 않도록 한다.

작업:

- WebSocket ticker 이벤트를 임시 queue 또는 `Map`에 적재
- 100ms 단위로 batch 적용
- Zustand store에 `applyTickerBatch` 액션 추가
- 종목 리스트는 store snapshot을 기준으로 렌더링

의미:

```text
ticker 이벤트 100개
  -> React state 업데이트 100번
```

이 아니라:

```text
ticker 이벤트 100개
  -> 100ms마다 React state 업데이트 1번
```

완료 기준:

- 빠른 ticker 이벤트에도 UI가 버벅이지 않는다.
- 테이블 값은 실시간에 가깝게 갱신된다.

## Phase 8. 전체 KRW ticker 확장

목표: 전체 KRW 마켓 ticker를 수집하고 오른쪽 종목 리스트에 표시한다.

작업:

- Upbit REST `GET /v1/market/all`로 전체 페어 목록 조회
- KRW 마켓 필터링
- 전체 KRW ticker WebSocket 구독
- 테이블 기본 정렬: 24시간 거래대금 내림차순
- 검색 구현

완료 기준:

- KRW 전체 종목이 오른쪽 리스트에 표시된다.
- 현재가, 전일 대비 가격/등락률, 24시간 거래대금이 표시된다.
- 검색과 정렬이 동작한다.

## Phase 9. 선택 종목 구독 관리

목표: 사용자가 종목을 선택하면 해당 종목의 상세 스트림만 구독한다.

작업:

- 프론트에서 `select-market` 이벤트 전송
- 백엔드 `client_state`에 선택 종목 저장
- `detail_subscriptions` 관리
- 선택 종목 `trade`, `orderbook`, `candle.{unit}` 구독
- 같은 종목을 여러 클라이언트가 선택해도 중복 구독하지 않음
- 선택 해제된 종목은 구독 집합에서 제거

완료 기준:

- 종목 선택 시 해당 종목 상세 데이터가 들어온다.
- 여러 클라이언트가 같은 종목을 선택해도 서버 내부 구독은 중복되지 않는다.
- 수신 데이터는 해당 종목을 보고 있는 클라이언트에게만 전달된다.

## Phase 10. 차트 초기/과거 데이터

목표: 선택 종목 차트를 REST 캔들 API로 표시한다.

작업:

- FastAPI `GET /api/candles` 구현
- Upbit REST 캔들 API 프록시
- 지원 단위 매핑
  - `1m`
  - `5m`
  - `15m`
  - `30m`
  - `60m`
  - `1d`
  - `1w`
- 초기 200개 캔들 로드
- 좌측 스크롤 시 `to=<oldest-candle-time>`으로 과거 200개 추가 로드
- lookback 제한은 설정값으로 관리하고 비활성화 가능하게 구성

완료 기준:

- 선택 종목의 캔들 차트가 표시된다.
- 시간 단위 변경 시 차트가 다시 로드된다.
- 왼쪽으로 이동하면 과거 캔들이 추가된다.
- 차트 내부에 거래량이 표시된다.

## Phase 11. 실시간 차트 업데이트

목표: WebSocket candle 이벤트로 마지막 캔들을 갱신한다.

작업:

- `candle:update` 이벤트 수신
- `market + unit + candle_date_time` 기준 upsert
- 같은 캔들 시간이 여러 번 와도 마지막 값을 최신으로 반영
- 선택한 시간 단위와 다른 candle 이벤트는 무시

완료 기준:

- 선택 종목 차트의 마지막 캔들이 실시간으로 갱신된다.
- 같은 캔들 시간이 중복 전송되어도 차트가 깨지지 않는다.

## Phase 12. 호가창과 최근 체결

목표: 선택 종목의 실시간 호가와 체결 내역을 표시한다.

작업:

- `orderbook:update` 이벤트 수신
- 매도/매수 호가 및 잔량 표시
- `trade:update` 이벤트 수신
- 최근 체결 N개 유지
- 체결 방향에 따라 색상 표시

완료 기준:

- 선택 종목 호가창이 실시간으로 갱신된다.
- 최근 체결 리스트가 최신 체결 순으로 표시된다.
- 종목 변경 시 이전 종목 상세 데이터가 섞이지 않는다.

## Phase 13. 알림 피드

목표: 전체 시장에서 주목할 만한 변화를 감지해 알림 피드에 표시한다.

작업:

- `AlertEngine` 구성
- 전일 대비 급등/급락 감지
- 최근 1분 가격 급변 감지
- `price_history: dict[market, deque]` 관리
- `alerts: deque[AlertEvent]` 관리
- `alert:new` 이벤트 전송

Workflow:

```text
Upbit ticker 수신
  -> MarketState 업데이트
  -> AlertEngine 검사
  -> 조건 만족 시 AlertEvent 생성
  -> alerts 저장
  -> Frontend에 alert:new 전송
```

완료 기준:

- 전일 대비 급등/급락 알림이 생성된다.
- 최근 1분 가격 급변 알림이 생성된다.
- 알림은 화면 피드에 누적 표시된다.
- 알림 임계값은 UI가 아니라 내부 설정값으로 관리된다.

## Phase 14. 연결 안정성

목표: 로컬 개발 중 WebSocket 끊김과 재연결 상황을 정상 처리한다.

작업:

- Upbit WebSocket reconnect/backoff
- Frontend WebSocket reconnect
- 서버 종료 시 연결 정리
- Upbit rate limit을 고려해 재연결 폭주 방지
- 연결 상태 UI 표시

완료 기준:

- Upbit 연결이 끊기면 백엔드가 자동 재연결한다.
- 프론트 연결이 끊기면 자동 재연결한다.
- 재연결 후 기존 구독 상태가 복구된다.

## Phase 15. 마무리 검증

목표: MVP를 로컬에서 안정적으로 실행할 수 있게 정리한다.

작업:

- README 실행 방법 작성
- `.env.example` 작성
- 백엔드 단위 테스트
  - ticker 파싱
  - MarketState 업데이트
  - AlertEngine 조건 판단
  - candle pagination 파라미터 생성
- 프론트 최소 테스트
  - 가격/등락률 포맷
  - ticker batch 적용
  - 종목 정렬
- 수동 E2E 확인
  - 서버 실행
  - 프론트 실행
  - 전체 종목 표시
  - 종목 선택
  - 차트/호가/체결/알림 확인

완료 기준:

- 로컬에서 프론트와 백엔드를 동시에 실행할 수 있다.
- 전체 KRW 종목 리스트가 실시간 갱신된다.
- 선택 종목 상세가 정상 갱신된다.
- 차트 과거 로딩이 동작한다.
- 주문 폼은 비활성 상태로 표시된다.

## MVP 이후로 미루는 것

- Redis
- DB
- 로그인
- 관심종목
- 실제 주문
- 모의투자 체결
- Vercel/Fly/Render 배포
- BTC/USDT 마켓 활성화
- 개인화 알림 설정
- 여러 차트 동시 보기

## 추천 첫 구현 단위

첫 구현은 다음 단위로 시작한다.

```text
FastAPI가 Upbit WebSocket에서 KRW-BTC/KRW-ETH ticker를 받고,
MarketState에 저장한 뒤,
GET /api/snapshot으로 최신 상태를 반환한다.
```

이 단위가 성공하면 다음 리스크를 빠르게 제거할 수 있다.

- 로컬에서 Upbit WebSocket 연결 가능 여부
- Upbit 메시지 파싱 방식
- 백엔드 상태 저장 구조
- REST snapshot 응답 구조
