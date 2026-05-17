# 공통 규칙

## 도메인

### REST

| 구분 | 도메인 |
| --- | --- |
| 운영 | https://api.kiwoom.com |

### WebSocket

| 구분 | 도메인 |
| --- | --- |
| 운영 | wss://api.kiwoom.com:10000 |

### 모의투자

| 도메인 |
| --- |
| https://mockapi.kiwoom.com(KRX만 지원가능) |
| wss://mockapi.kiwoom.com:10000(KRX만 지원가능) |

## 인증 흐름

1. `au10001` 접근토큰 발급 API로 `appkey`, `secretkey`를 전달해 접근토큰을 발급합니다.
2. 이후 API 호출 시 Header `authorization`에 `Bearer <token>` 형식으로 접근토큰을 전달합니다.
3. 필요 시 `au10002` 접근토큰폐기 API로 토큰을 폐기합니다.

## 공통 Header

| Header | 필수 | 설명 |
| --- | --- | --- |
| api-id | Y | 호출할 API ID 또는 실시간 항목 ID |
| authorization | Y | Bearer 접근토큰 |
| cont-yn | N | 응답 Header의 연속조회여부가 Y인 경우 다음 조회 요청에 사용 |
| next-key | N | 응답 Header의 연속조회키가 있는 경우 다음 조회 요청에 사용 |

## 연속조회

응답 Header의 `cont-yn` 값이 `Y`이면 다음 데이터가 있다는 뜻입니다. 다음 요청 Header에 응답으로 받은 `cont-yn`, `next-key` 값을 넣어 이어서 조회합니다.

## 응답 공통값

대부분의 예시 응답은 Body에 `return_code`, `return_msg`를 포함합니다. 오류 상세는 [error-codes.md](error-codes.md)를 기준으로 확인합니다.
