# Deprecated API 인덱스

정리일: 2026-05-29  
대상: 업비트 Deprecated API

## 문서 목록

| 파일 | 원문 | 내용 | 대체 권장 |
| --- | --- | --- | --- |
| [orderbook-levels.md](./orderbook-levels.md) | [호가 모아보기 단위 조회](https://docs.upbit.com/kr/reference/list-orderbook-levels) | `GET /v1/orderbook/supported_levels`, 페어별 지원 `level` 조회 | [호가 정책 조회](../quotation/orderbooks.md) |

## 운영 메모

- Deprecated API는 기존 코드 이해와 유지보수를 위해 문서화한다.
- 신규 기능 구현에서는 Deprecated API 사용을 피하고 대체 API를 우선 검토한다.
- Rate Limit은 대체 API와 같은 그룹을 공유할 수 있으므로 호출량 관리에서 별도 예외로 보지 않는다.
