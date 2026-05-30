# 업비트 대시보드 로컬 개발

## 구조

```text
apps/
  web/      Next.js frontend
  backend/  FastAPI backend
```

실행 가능한 앱은 `apps/` 아래에 모은다. 루트에는 프론트 workspace나 백엔드 pyproject를 두지 않는다. 루트 `Makefile`은 로컬 실행 명령만 중계한다.

## 백엔드

```bash
uv sync --directory apps/backend
make dev-api
```

기본 주소:

```text
http://localhost:8000
```

Health check:

```bash
make health-api
```

## 프론트엔드

```bash
pnpm -C apps/web install
make dev-web
```

기본 주소:

```text
http://localhost:3000
```

Next.js Route Handler health check:

```bash
make health-web
```

## 동시 실행

```bash
make dev
```

`apps/web/.env.local.example`을 `apps/web/.env.local`로 복사하면 `FASTAPI_BASE_URL`을 로컬 환경에 맞게 조정할 수 있다.
