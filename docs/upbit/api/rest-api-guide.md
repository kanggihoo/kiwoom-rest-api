# 업비트 REST API 사용 및 에러 안내

출처: https://docs.upbit.com/kr/reference/rest-api-guide  
정리일: 2026-05-29

## Endpoint

```text
https://api.upbit.com/v1
```

## TLS

- TLS 1.2 이상만 지원한다.
- TLS 1.3 사용을 권장한다.

## Content Type

- REST API는 `application/json` Content Type을 지원한다.
- POST 요청은 JSON body로 전송해야 한다.

```http
Content-Type: application/json; charset=utf-8
```

- POST API의 Form 방식 요청은 2022-03-01부터 지원이 종료되었다.
- Urlencoded Form 방식 POST 요청의 정상 동작은 보장되지 않는다.

## 인증

Exchange API 요청에는 JWT 토큰을 `Authorization` 헤더에 포함해야 한다.

```http
Authorization: Bearer <JWT_TOKEN>
```

인증 토큰 생성 규칙은 [auth.md](./auth.md)를 참고한다.

## 요청 수 제한

REST API 요청 수 제한은 API 그룹별로 적용된다. 구현 시 `Remaining-Req` 응답 헤더를 활용해야 한다. 자세한 내용은 [rate-limits.md](./rate-limits.md)를 참고한다.

## 응답 상태 코드

| HTTP 상태 | 주요 의미 | 처리 방향 |
| --- | --- | --- |
| 200 OK | 정상 응답 | 정상 처리 |
| 201 Created | 요청으로 인한 생성 완료 | 정상 처리 |
| 400 Bad Request | 잘못된 요청, 주문 조건 오류, 잔고 부족, 최소 주문 금액 미달 등 | 요청 파라미터와 주문 조건 확인 |
| 401 Unauthorized | JWT 페이로드 오류, JWT 검증 실패, 만료된 API Key, 재사용 nonce, 미등록 IP, 토큰 누락 | 인증 생성 로직과 API Key/IP 설정 확인 |
| 403 Forbidden | 권한 범위 초과 | API Key 권한 그룹 확인 |
| 404 Not Found | 존재하지 않는 주문/출금/입금/체결 등 | 요청 대상 식별자 확인 |
| 418 I'm a teapot | 과도한 요청으로 일시 차단 | 차단 시간 이후 재시도 |
| 429 Too Many Requests | 요청 제한 초과 | 백오프 후 재시도 |
| 500 Internal Server Error | 서버 내부 오류 또는 점검 | 재시도 정책 또는 장애 처리 |

## 주요 에러 코드

| 상태 | 에러 코드 | 의미 | 대응 |
| --- | --- | --- | --- |
| 400 | `create_ask_error`, `create_bid_error` | 주문 요청 정보가 올바르지 않음 | 주문 타입별 필수/금지 필드 확인 |
| 400 | `insufficient_funds_ask`, `insufficient_funds_bid` | 매수/매도 가능 잔고 부족 | 잔고 확인 |
| 400 | `under_min_total_ask`, `under_min_total_bid` | 최소 주문 금액 미달 | 페어별 최소 주문 금액 확인 |
| 400 | `withdraw_address_not_registered` | 허용되지 않은 출금 주소 | 출금 허용 주소 등록 여부 확인 |
| 400 | `validation_error` | 필수 파라미터 누락 등 잘못된 요청 | 요청 스키마 확인 |
| 401 | `invalid_query_payload` | JWT 페이로드가 올바르지 않음 | `query_hash`, payload 구성 확인 |
| 401 | `jwt_verification` | JWT 검증 실패 | 서명 알고리즘, Secret Key 확인 |
| 401 | `expired_access_key` | API Key 만료 | 새 API Key 발급 |
| 401 | `nonce_used` | 이미 사용된 nonce | 매 요청 새 nonce 사용 |
| 401 | `no_authorization_ip` | 등록되지 않은 IP | API Key 허용 IP 확인 |
| 401 | `no_authorization_token` | 인증 토큰 누락 | Authorization 헤더 확인 |
| 403 | `out_of_scope` | API Key 권한 범위 초과 | 필요한 권한 부여 |

Quotation API의 `error.name`은 정수형일 수 있고, Exchange API의 `error.name`은 문자열형일 수 있다. 예외 처리는 HTTP 상태 코드만이 아니라 에러 코드 문자열도 함께 보는 것이 좋다.

## 에러 응답 형식

```json
{
  "error": {
    "name": "ERROR_CODE",
    "message": "ERROR_MESSAGE"
  }
}
```

## 인코딩

- GET 또는 DELETE 요청에 쿼리 파라미터가 있으면 모든 쿼리 파라미터를 URL 인코딩해야 한다.
- 인코딩이 잘못되면 400 `Invalid parameter`가 발생할 수 있다.
- Exchange API에서 배열 파라미터 이름에 `[]`가 포함된 경우 `[`와 `]`는 인코딩하지 않는다.

예:

```text
states[]=wait&states[]=watch
```

## gzip 응답

시세(Quotation) API는 gzip 응답을 지원한다.

```http
Accept-Encoding: gzip
```

gzip을 사용하면 응답 데이터 크기와 트래픽 비용을 줄일 수 있다.

## API Reference 예제 코드

- 각 API Reference는 Shell(cURL), Python, Java, Node.js 예제를 제공한다.
- Java 예제는 AsyncHttp, `java.net.http`, OkHttp, Unirest 등으로 나뉠 수 있다.
- Node.js 예제는 Axios, fetch, https 등으로 나뉠 수 있다.
- Exchange API 예제 코드에는 인증 토큰 생성 부분이 제외될 수 있으므로 실제 연동 시 [auth.md](./auth.md)의 JWT 생성 규칙을 반드시 적용한다.
