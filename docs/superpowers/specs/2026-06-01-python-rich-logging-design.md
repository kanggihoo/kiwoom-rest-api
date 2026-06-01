# Python Rich 로깅 설정 설계

## 작성일

2026-06-01

## 배경

현재 FastAPI 백엔드는 `apps/backend` 아래의 독립 `uv` Python 프로젝트로 관리된다. 앱 진입점은 `apps/backend/src/upbit_dashboard/main.py`이고, 로컬 개발 실행은 루트 `Makefile`의 `dev-api` 타깃에서 `uvicorn upbit_dashboard.main:app --reload`로 수행한다.

기존 Python 코드는 `logging.getLogger(__name__)` 패턴을 이미 사용하고 있다. 그러나 공통 로깅 설정 파일은 아직 없고, `upbit_dashboard.tools.smoke_upbit_connection`은 자체적으로 `logging.basicConfig(...)`를 호출한다. 이 때문에 FastAPI 앱, uvicorn 로그, smoke tool 로그를 동일한 정책으로 관리하기 어렵다.

## 목표

Python 표준 로깅 모듈인 `logging`을 기준으로 FastAPI 앱 로그와 uvicorn 로그를 한 번에 설정한다.

로컬 개발 디버깅 목적으로만 Rich 색상 로그를 사용할 수 있게 한다.

로그 레벨, 로그 포맷, uvicorn 관련 로거 설정을 하나의 Python 파일에서 관리한다.

여러 번 설정 함수가 호출되거나 uvicorn reload 프로세스에서 앱이 다시 로드되어도 중복 핸들러가 생기지 않게 한다.

## 비목표

운영 환경용 JSON 로그 포맷은 이번 범위에 포함하지 않는다.

파일 로그 저장, 로그 로테이션, 외부 로그 수집기 연동은 이번 범위에 포함하지 않는다.

Upbit quotation 도메인 로직, API 계약, WebSocket 처리 방식은 변경하지 않는다.

Next.js BFF Route Handler 로그 정책은 이번 범위에 포함하지 않는다.

## 환경변수

`LOG_FORMAT`은 로그 출력 방식을 결정한다.

기본값은 `plain`이다.

허용 값은 `plain`, `rich`이다.

`LOG_FORMAT=rich`일 때만 Rich 기반 컬러 콘솔 로그를 사용한다.

`LOG_LEVEL`은 전체 Python 로그 레벨을 결정한다.

기본값은 `INFO`이다.

대표 사용 예시는 `LOG_FORMAT=rich LOG_LEVEL=DEBUG make dev-api`이다.

알 수 없는 `LOG_FORMAT` 값은 `plain`으로 fallback한다.

알 수 없는 `LOG_LEVEL` 값은 `INFO`로 fallback한다.

## 의존성

`apps/backend/pyproject.toml`의 런타임 의존성에 `rich`를 추가한다.

Rich는 `LOG_FORMAT=rich`일 때만 핸들러로 사용한다.

## 파일 구조

새 파일 `apps/backend/src/upbit_dashboard/logging_config.py`를 추가한다.

이 파일은 로깅 설정의 단일 진입점이다.

주요 공개 함수는 `configure_logging()`이다.

내부 헬퍼로 `build_logging_config()`, `get_log_format()`, `get_log_level()` 같은 작은 함수를 둘 수 있다.

파일명은 `logging.py`를 사용하지 않는다. 표준 라이브러리 `logging`과 이름이 겹쳐 import 가독성과 디버깅을 해칠 수 있기 때문이다.

## 설정 방식

`logging.config.dictConfig(...)`를 사용한다.

외부 YAML 또는 JSON 설정 파일은 만들지 않는다.

Python 파일 안에서 환경변수를 읽고 `dictConfig` 딕셔너리를 구성한다.

`plain`과 `rich` 설정은 같은 함수에서 분기한다.

## plain 로그 포맷

기본 `plain` 포맷은 터미널과 CI에서 깨지지 않는 일반 텍스트를 출력한다.

권장 포맷은 다음 정보들을 포함한다.

```text
%(asctime)s %(levelname)-8s [%(name)s] %(message)s
```

권장 날짜 포맷은 다음과 같다.

```text
%Y-%m-%d %H:%M:%S
```

예상 출력 예시는 다음과 같다.

```text
2026-06-01 12:34:56 INFO     [upbit_dashboard.upbit.runner] Upbit ticker stream starting markets=KRW-BTC,KRW-ETH
```

## rich 로그 포맷

`rich.logging.RichHandler`를 사용한다.

Rich 로그는 로컬 개발 디버깅 가독성을 우선한다.

권장 설정은 다음과 같다.

```text
rich_tracebacks=True
show_time=True
show_level=True
show_path=True
enable_link_path=True
markup=False
```

`markup=False`를 사용해 애플리케이션 로그 메시지 안의 대괄호 문자열이 Rich markup으로 해석되지 않게 한다.

RichHandler는 `show_path=True`일 때 로그를 호출한 파일과 라인 번호를 path column에 표시한다.

formatter는 RichHandler의 컬럼 렌더링과 충돌하지 않도록 `%(message)s`만 사용한다.

예상 출력 방향은 다음과 같다.

```text
[06/01/26 12:34:56] INFO     Upbit ticker stream starting markets=KRW-BTC,KRW-ETH  runner.py:63
```

정확한 색상, 시간 표현, path column 표현은 RichHandler의 기본 렌더링에 따른다.

## 적용 대상 로거

`root` 로거를 설정한다.

`upbit_dashboard` 로거를 설정한다.

`uvicorn` 로거를 설정한다.

`uvicorn.error` 로거를 설정한다.

`uvicorn.access` 로거를 설정한다.

이 로거들은 동일한 콘솔 핸들러와 로그 레벨 정책을 공유한다.

중복 출력을 막기 위해 명시적으로 설정한 uvicorn 계열 로거는 `propagate=False`로 둔다.

## uvicorn 로그 통합

FastAPI 앱 실행은 `uvicorn upbit_dashboard.main:app --reload` 형태로 이루어진다.

`main.py` 모듈 import 시점에 `configure_logging()`을 호출해 uvicorn이 앱을 로드할 때 공통 로깅 설정이 적용되게 한다.

uvicorn이 자체 기본 로깅 설정을 먼저 구성할 수 있으므로 `configure_logging()`은 기존 핸들러 상태에 의존하지 않고 `dictConfig`로 최종 상태를 덮어쓴다.

`disable_existing_loggers`는 `False`로 둔다. 라이브러리 로거를 무조건 비활성화하지 않기 위해서다.

## 앱 적용 지점

`apps/backend/src/upbit_dashboard/main.py`에서 앱 로거를 생성하기 전에 `configure_logging()`을 호출한다.

기존 `logger = logging.getLogger(__name__)` 패턴은 유지한다.

FastAPI lifespan 내부의 기존 로그 호출은 변경하지 않는다.

## smoke tool 적용 지점

`apps/backend/src/upbit_dashboard/tools/smoke_upbit_connection.py`의 `logging.basicConfig(...)` 호출을 제거한다.

대신 `configure_logging()`을 호출한다.

이로써 `make upbit-smoke` 실행도 `LOG_FORMAT`과 `LOG_LEVEL` 정책을 동일하게 따른다.

## 에러 처리와 fallback

`LOG_FORMAT=rich`인데 Rich import가 실패하는 상황은 의존성 누락 상태로 간주한다.

구현에서는 명확한 `RuntimeError`를 발생시켜 설치 상태를 바로잡게 한다.

이번 프로젝트에서는 `rich`를 런타임 의존성에 추가하므로 정상 설치 환경에서는 Rich import 실패가 없어야 한다.

`LOG_LEVEL` 값이 Python logging 표준 레벨명이 아니면 `INFO`로 처리한다.

`LOG_FORMAT` 값이 `plain` 또는 `rich`가 아니면 `plain`으로 처리한다.

## 테스트와 검증 범위

구현 후에는 로깅 설정 딕셔너리 생성 함수를 단위 테스트할 수 있다.

검증할 항목은 기본값, `LOG_FORMAT=rich`, 알 수 없는 `LOG_FORMAT`, `LOG_LEVEL=DEBUG`, 알 수 없는 `LOG_LEVEL`이다.

FastAPI 앱 import 테스트는 기존 lifespan과 충돌하지 않아야 한다.

실행 검증은 다음 명령으로 가능하다.

```bash
make dev-api
LOG_FORMAT=rich LOG_LEVEL=DEBUG make dev-api
LOG_FORMAT=rich LOG_LEVEL=DEBUG make upbit-smoke
```

## 수용 기준

기본 실행에서 일반 텍스트 로그가 출력된다.

`LOG_FORMAT=rich` 실행에서 Rich 컬러 로그가 출력된다.

`LOG_LEVEL=DEBUG` 실행에서 디버그 레벨 설정이 적용된다.

FastAPI 앱 로그와 uvicorn access/error 로그가 같은 정책으로 출력된다.

uvicorn reload 시 로그가 중복 출력되지 않는다.

smoke tool이 FastAPI 앱과 같은 로깅 설정을 사용한다.

로깅 설정은 `apps/backend/src/upbit_dashboard/logging_config.py` 한 파일에서 관리된다.
