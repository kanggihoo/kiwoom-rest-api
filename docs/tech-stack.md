# 업비트 대시보드 기술 스택

정리일: 2026-05-29

## 확정 스택

### Frontend

- Next.js
- TypeScript
- Tailwind CSS
- lightweight-charts
- Zustand
- TanStack Query
- pnpm

### Backend

- Python 3.12+
- FastAPI
- Uvicorn
- websockets
- Pydantic
- pytest
- uv

### Local Infra

- DB 없음
- Redis 없음
- Backend 상태는 process memory 사용
- Frontend dev server: `http://localhost:3000`
- Backend API/WebSocket server: `http://localhost:8000`

## 로컬 개발 구조

```text
Upbit WebSocket
      │
      ▼
FastAPI + Uvicorn
http://localhost:8000
ws://localhost:8000/ws
      │
      ▼
Next.js
http://localhost:3000
```

## 역할 분리

### Next.js

- 화면 렌더링
- 전체 종목 리스트
- 선택 종목 상세 패널
- 차트
- 호가창
- 최근 체결 내역
- 알림 피드
- 비활성 주문 폼 UI
- Backend WebSocket 수신
- Next.js Route Handler를 통한 REST BFF 제공

### FastAPI

- Upbit WebSocket 연결 유지
- 전체 KRW ticker 수집
- 선택 종목 trade/orderbook/candle 수집
- 최신 ticker snapshot 관리
- 선택 종목 구독 상태 관리
- 알림 이벤트 계산
- Frontend WebSocket gateway 제공
- 마켓 목록, 캔들 조회, 스냅샷 REST API 제공

## 통신 방식

### Upbit -> Backend

WebSocket을 사용한다.

- 공개 시세 데이터만 사용
- 인증 없음
- `ticker`, `trade`, `orderbook`, `candle.{unit}` 사용

### Backend -> Frontend

WebSocket을 사용한다.

브라우저는 FastAPI WebSocket endpoint에 직접 연결한다.

```text
Next Frontend
  -> FastAPI WebSocket
```

서버에서 프론트로 보내는 이벤트 예:

- `ticker:update`
- `trade:update`
- `orderbook:update`
- `candle:update`
- `alert:new`

프론트에서 서버로 보내는 이벤트 예:

- `select-market`
- `change-candle-unit`
- `subscribe`
- `unsubscribe`

### REST API

초기 데이터와 과거 데이터 조회에 사용한다.

REST 요청은 브라우저가 FastAPI를 직접 호출하지 않고 Next.js Route Handler를 경유한다.

```text
Next Frontend
  -> Next.js Route Handler
  -> FastAPI REST API
```

- `GET /api/markets`
- `GET /api/snapshot`
- `GET /api/candles`

로컬 개발 시 프론트는 REST를 상대 경로(`/api/...`)로 호출하고, Next.js 서버는 내부 환경변수의 FastAPI URL로 프록시한다.

## 저장소 구조

```text
apps/
  web/        # Next.js
  backend/    # FastAPI

docs/
  upbit/
```

실행 가능한 앱은 `apps/` 아래에 모은다. 루트에는 `package.json`, `pnpm-workspace.yaml`, 업비트용 `pyproject.toml`을 두지 않는다. 루트 `Makefile`은 로컬 실행 명령만 중계한다.

`packages/shared`는 MVP에서 필수는 아니다. 프론트와 백엔드 언어가 달라 TypeScript 타입 공유 효과가 제한적이므로, 초기에는 OpenAPI/Pydantic 모델과 문서화로 스키마를 관리한다.

## 상태 관리

MVP에서는 DB와 Redis 없이 백엔드 메모리에 상태를 둔다.

예:

```text
tickers: dict[market, Ticker]
client_state: dict[client_id, ClientState]
detail_subscriptions: dict[market, set[client_id]]
price_history: dict[market, deque]
alerts: deque[AlertEvent]
```

서버 재시작 시 상태는 초기화된다. MVP에서는 허용한다.

## Redis 도입 기준

MVP에서는 Redis를 사용하지 않는다. 다음 요구가 생기면 도입을 검토한다.

- 백엔드 인스턴스를 여러 개 띄워야 함
- 최신 ticker snapshot을 서버 재시작 후에도 유지해야 함
- 최근 알림을 공유/보존해야 함
- 캔들 REST 응답 캐시가 필요함
- 여러 백엔드 인스턴스 간 이벤트 브로드캐스트가 필요함
- 알림 중복 방지를 TTL 기반으로 처리하고 싶음

도입 시 우선순위:

```text
1. 캔들 API 응답 캐시
2. 최근 알림 저장
3. 최신 ticker snapshot 저장
4. Pub/Sub 또는 Streams 기반 fanout
```

## 배포 계획

MVP 배포는 범위에 포함하지 않는다. 로컬 개발 완료 후 필요하면 다음 구성을 검토한다.

```text
Frontend: Vercel
Backend: Fly.io 또는 Render
Redis: 필요 시 Upstash/Redis Cloud/managed Redis
DB: 로그인, 모의투자, 개인화 기능이 생기면 PostgreSQL 검토
```

Vercel은 프론트 배포에 사용한다. Vercel Functions는 WebSocket 서버 역할에 적합하지 않으므로 Backend WebSocket 서버는 별도 서버형 런타임에 둔다.

## 선택 이유

- Next.js는 대시보드 UI, 라우팅, 배포 경로가 단순하다.
- FastAPI는 WebSocket과 REST API를 모두 구현하기 쉽고 Python 비동기 생태계를 활용할 수 있다.
- pnpm과 uv를 사용해 프론트/백엔드 의존성 관리를 명확히 분리한다.
- DB/Redis를 제외해 로컬 MVP 복잡도를 낮춘다.
- REST는 Next.js BFF를 경유해 브라우저 CORS 부담을 줄이고, WebSocket은 FastAPI에 직접 연결해 실시간 경로를 단순하게 유지한다.
- WebSocket 백엔드를 별도 프로세스로 두면 로컬 개발과 추후 배포 구조가 자연스럽게 이어진다.
