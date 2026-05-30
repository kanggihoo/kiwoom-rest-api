# 업비트 API 인증

출처: https://docs.upbit.com/kr/reference/auth  
정리일: 2026-05-29

## 핵심 요약

Exchange REST API와 Private WebSocket은 API Key 기반 JWT 인증이 필요하다. Quotation 조회 API는 공개 API라 인증 없이 사용할 수 있다.

## API Key

- API Key는 Access Key와 Secret Key 쌍으로 구성된다.
- Secret Key는 발급 시점에만 확인 가능하므로 안전하게 보관해야 한다.
- API Key 발급 시 호출지 IP를 허용 목록에 등록해야 하며, API Key 하나당 최대 10개의 IP를 등록할 수 있다.
- 토큰 생성에는 반드시 서로 짝이 맞는 Access Key와 Secret Key를 사용한다.
- 필요한 권한만 부여하는 방식으로 API Key를 발급하는 것이 좋다.

## 권한 그룹

| 권한 그룹 | 주요 REST API | WebSocket |
| --- | --- | --- |
| 권한 없음 | 통화별 입출금 서비스 상태 조회, API Key 목록 조회 | 없음 |
| 자산조회 | 계정 잔고 조회 | `myAsset` |
| 주문하기 | 주문 생성, 주문 생성 테스트, 주문 취소, 일괄 취소, 취소 후 재주문 | 없음 |
| 주문조회 | 주문 가능정보, 단일 주문, 주문 목록, 체결 대기/종료 주문 조회 | `myOrder` |
| 출금하기 | 디지털 자산 출금, 원화 출금, 출금 취소 | 없음 |
| 출금조회 | 출금 가능 정보, 출금 허용 주소, 단일 출금, 출금 목록 조회 | 없음 |
| 입금하기 | 원화 입금, 트래블룰 검증 요청 | 없음 |
| 입금조회 | 입금 주소 생성/조회, 입금 가능 통화, 입금 목록, 트래블룰 지원 거래소 조회 | 없음 |

## JWT 구조

JWT는 Header, Payload, Signature로 구성된다.

### Header

```json
{
  "alg": "HS512",
  "typ": "JWT"
}
```

- 서명 알고리즘은 `HS512` 사용을 권장한다.

### Payload

| 필드 | 필수 여부 | 설명 |
| --- | --- | --- |
| `access_key` | 필수 | API Key의 Access Key |
| `nonce` | 필수 | 매 요청마다 새로 생성하는 UUID 문자열 |
| `query_hash` | 조건부 필수 | REST 요청에 쿼리 파라미터나 본문이 있을 때 쿼리 문자열을 SHA512로 해시한 값 |
| `query_hash_alg` | 선택 | `query_hash` 알고리즘. 기본은 `SHA512` |

파라미터나 본문이 없는 REST 요청, WebSocket 인증에는 `access_key`, `nonce`만 포함하면 된다.

### Signature

- Secret Key로 Header와 Payload를 서명한다.
- Secret Key는 Base64 인코딩된 값이 아니므로 별도 Base64 디코딩을 하지 않는다.
- JWT 라이브러리 사용 시 Secret Key를 그대로 HMAC 키로 전달한다.

## query_hash 생성 규칙

`query_hash`는 실제 요청 파라미터와 동일한 쿼리 문자열을 기준으로 생성해야 한다. 순서나 표현이 달라지면 인증 실패가 발생할 수 있다.

### GET/DELETE

- 실제 URL에 포함될 쿼리 문자열을 그대로 사용한다.
- 파라미터 순서를 재정렬하지 않는다.
- `states[]`, `uuids[]`처럼 이름에 `[]`가 포함된 배열 파라미터는 `states[]=wait&states[]=watch`처럼 key-value를 반복한다.
- `pairs`, `quote_currencies`처럼 쉼표 구분 문자열을 받는 파라미터는 `pairs=KRW-BTC,KRW-ETH` 형태로 구성한다.
- 해시는 URL 인코딩 전 쿼리 문자열 기준으로 생성한다.

예:

```text
market=KRW-BTC&limit=10
market=KRW-BTC&states[]=wait&states[]=watch
```

### POST

JSON 본문의 모든 key-value를 쿼리 문자열 형태로 변환한 뒤 SHA512 해시를 만든다.

```json
{
  "market": "KRW-BTC",
  "side": "bid",
  "volume": "0.01",
  "price": "100.0",
  "ord_type": "limit"
}
```

위 본문은 다음 문자열로 해시한다.

```text
market=KRW-BTC&side=bid&volume=0.01&price=100.0&ord_type=limit
```

## 인증 헤더

REST API와 WebSocket 모두 동일하게 Bearer 인증을 사용한다.

```http
Authorization: Bearer <JWT_TOKEN>
```

## 구현 체크리스트

- 매 요청마다 새로운 `nonce`를 사용한다.
- 요청에 파라미터 또는 body가 있으면 반드시 `query_hash`를 포함한다.
- `query_hash`의 원문 문자열과 실제 요청 문자열의 순서 및 표현을 일치시킨다.
- Secret Key를 Base64 디코딩하지 않는다.
- 주문/입출금 기능을 호출하기 전 API Key 권한 그룹을 확인한다.
