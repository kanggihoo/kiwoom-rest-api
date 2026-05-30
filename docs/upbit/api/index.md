# 업비트 API 문서 인덱스

정리일: 2026-05-29  
대상: 업비트 개발자 센터 API Reference v1.6.2

## 문서 목록

| 파일 | 원문 | 내용 |
| --- | --- | --- |
| [overview.md](./overview.md) | [개요](https://docs.upbit.com/kr/reference/api-overview) | Quotation/Exchange 구분, REST/WebSocket 선택 기준, 기능 분류 |
| [auth.md](./auth.md) | [인증](https://docs.upbit.com/kr/reference/auth) | API Key, 권한 그룹, JWT 구조, `query_hash` 생성 규칙, 인증 헤더 |
| [rate-limits.md](./rate-limits.md) | [요청 수 제한](https://docs.upbit.com/kr/reference/rate-limits) | 제한 단위, Rate Limit 그룹, `Remaining-Req` 헤더, 429/418 처리 |
| [rest-api-guide.md](./rest-api-guide.md) | [REST API 사용 및 에러 안내](https://docs.upbit.com/kr/reference/rest-api-guide) | REST Endpoint, TLS, Content Type, 상태 코드, 에러 코드, 인코딩, gzip |
| [websocket-guide.md](./websocket-guide.md) | [WebSocket 사용 및 에러 안내](https://docs.upbit.com/kr/reference/websocket-guide) | WebSocket Endpoint, 인증, 요청 메시지 구조, 포맷, 연결 유지, 에러 코드 |
| [dashboard-mvp.md](./dashboard-mvp.md) | 내부 기획 문서 | 업비트 실시간 모니터링 대시보드 MVP 목표, 레이아웃, 데이터 흐름, 기능 범위 |
| [tech-stack.md](./tech-stack.md) | 내부 기술 결정 문서 | Next.js/FastAPI 기반 로컬 MVP 기술 스택, 통신 방식, 상태 관리, 배포 후보 |
| [quotation/index.md](./quotation/index.md) | Quotation API Reference | 페어, 캔들, 체결, 현재가, 호가 REST API 요약 |
| [websocket/index.md](./websocket/index.md) | WebSocket API Reference | 현재가, 체결, 호가, 캔들, 내 주문/자산, 구독 목록 조회 요약 |
| [deprecated/index.md](./deprecated/index.md) | Deprecated API Reference | 호가 모아보기 단위 조회 등 Deprecated API와 대체 권장 API |

## 빠른 참조

### 공개 시세 조회

- 인증 없이 Quotation REST API 사용 가능
- WebSocket 실시간 시세도 공개 Endpoint 사용 가능
- 요청 제한은 주로 IP 단위로 적용

관련 문서:

- [overview.md](./overview.md)
- [rate-limits.md](./rate-limits.md)
- [quotation/index.md](./quotation/index.md)
- [websocket-guide.md](./websocket-guide.md)
- [websocket/index.md](./websocket/index.md)

### 주문/잔고/입출금

- Exchange API 사용
- API Key와 JWT 인증 필수
- API Key 권한 그룹과 허용 IP를 먼저 확인
- 주문 생성 계열은 별도 Rate Limit 그룹이 적용됨

관련 문서:

- [auth.md](./auth.md)
- [rate-limits.md](./rate-limits.md)
- [rest-api-guide.md](./rest-api-guide.md)
- [websocket/index.md](./websocket/index.md)

### 인증 구현

- `Authorization: Bearer <JWT_TOKEN>` 헤더 사용
- 매 요청마다 새 `nonce` 사용
- 쿼리 파라미터나 JSON body가 있으면 `query_hash` 포함
- Secret Key는 Base64 디코딩하지 않음

관련 문서:

- [auth.md](./auth.md)
- [rest-api-guide.md](./rest-api-guide.md)

### 요청 제한 처리

- REST 응답의 `Remaining-Req` 헤더에서 `sec` 값을 확인
- 제한 초과 시 `429`, 지속 초과 또는 차단 시 `418`
- WebSocket은 연결 요청과 메시지 전송 제한을 별도로 관리

관련 문서:

- [rate-limits.md](./rate-limits.md)
- [websocket-guide.md](./websocket-guide.md)

## 파일 작성 기준

- 원문을 그대로 복사하지 않고 구현에 필요한 핵심 정책, 표, 체크리스트 중심으로 재정리했다.
- API별 상세 요청/응답 스키마는 각 개별 Reference 문서를 추가로 확인해야 한다.
- Rate Limit과 권한 정책은 서비스 공지에 따라 변경될 수 있으므로 실제 배포 전 원문을 재확인한다.
- Deprecated API는 기존 구현 유지보수 목적의 참고 문서로 두고 신규 구현에서는 대체 API를 우선한다.
