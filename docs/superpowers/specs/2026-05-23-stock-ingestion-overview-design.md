# 재고 수집 개요 디자인

작성일: 2026-05-23

## 목적

Cloudflare 무료 요금제와 Supabase 무료 요금제만 사용해서 국장/미장 관심의 OHLCV 데이터를 수집하고 생성합니다. 기본 목표는 40~50개를 10분마다 수집하는 경향입니다. 이후 5분 또는 1분 수집으로 확실히 구조가 열릴 수는 있지만, 더 조심스럽게 전환하는 것은 아닙니다.

## 열심히 활동하다

- 외부 주식 API는 일괄 호출을 지원하지 않고 1회 호출해야 합니다.
- Cloudflare Workers 무료 요금제의 외부 하위 요청을 제한하여 한 번만 Worker 실행에서 모든 곡선을 항상 처리할 수 없습니다.
- Supabase Free 요금제의 DB 용량 한도를 강력하게 원본성 인트라데이 데이터는 현재 보관하고 상위 위치로 롤업합니다.
- 컨트롤러 전환은 허용되지 않습니다. quota에 가까워지면 수집량, 보관 기간, 수집기를 줄인다.
- 초기 수집자는 교육장만 대상으로 합니다. 시간외 거래는 `session_type`으로 확장 가능하게만 처리됩니다.

##필요하게

```txt
Cloudflare Cron Worker
  -> market calendar/session check
  -> Supabase watchlist 조회
  -> priority 높은 종목부터 API 호출
  -> OHLCV normalize
  -> Supabase batch upsert
  -> ingestion 상태 기록
  -> KV에 마지막 상태 요약 저장

Supabase Postgres
  -> stock_price_bars 저장
  -> pg_cron rollup/delete
  -> health/status view 제공

Grafana
  -> Supabase Metrics API
  -> Cloudflare Workers OTel/Logs
  -> Supabase 상태 테이블/view 조회
```

## 분리

Cloudflare Worker는 외부 API 호출과 10분봉 수집만을 담당합니다. Worker가 30분봉, 1시간봉, 일봉을 직접 포함합니다.

Supabase는 데이터 저장, 고유/upsert 기반 구문 방지, pg_cron 기반 롤업/삭제, 상태 조회 보기를 담당합니다.

KV는 최종 상태가 아닙니다. 마지막 실행 잘, 마지막 커서, 간단한 건강 요약 같은 보조 상태를 저장합니다. 추출하는 것을 방지하려면 DB 고유 키와 upsert를 담당해야 합니다.

## 일부러

- 원천수집대상: 국장 + 미장 관심 종목 40~50개.
- 수집기: 10분. 이후 줄일 수 있게 설계한다.
- API 호출 방식: 종목당 1회 호출.
- 선택하는 방식: 순수 priority. priority가 낮은 종목은 free quota 때문에 계속 밀릴 수 있다.
- 수집시간: 시장별 정규장만.
- 저장 데이터: OHLCV만. 원본 API JSON은 저장하지 않는다.
- 보관: 10분봉은 30일, 30분봉은 180일, 1시간봉은 1~2년, 일봉은 장기 보관.
- 예측: 상태 테이블과 Grafana 연동 전제를 포함한다. 알림은 후속 확장이다.

## 축소 원칙

쿼리할 수 있거나 수집하기 위해 먼저 무료 할당량을 포함하도록 합니다. 할당량이 없으면 다음 시간으로 조정합니다.

1. 우선순위 제외.
2. 수집작업b.
3. 장중 보관기간 단축.
4. 상위에 응답하고 더 낮은 기간을 삭제합니다.

경계 전환은 확장 도구를 사용하지 않는 것입니다.
