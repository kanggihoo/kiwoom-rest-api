# Quotation API 인덱스

정리일: 2026-05-29  
대상: 업비트 Quotation REST API

## 문서 목록

| 파일 | 원문 | 내용 |
| --- | --- | --- |
| [trading-pairs.md](./trading-pairs.md) | [페어 목록 조회](https://docs.upbit.com/kr/reference/list-trading-pairs) | 거래 가능한 페어 목록, `is_details`, 마켓 그룹 Rate Limit |
| [candles.md](./candles.md) | [초](https://docs.upbit.com/kr/reference/list-candles-seconds), [분](https://docs.upbit.com/kr/reference/list-candles-minutes), [일](https://docs.upbit.com/kr/reference/list-candles-days), [주](https://docs.upbit.com/kr/reference/list-candles-weeks), [월](https://docs.upbit.com/kr/reference/list-candles-months), [연](https://docs.upbit.com/kr/reference/list-candles-years) 캔들 조회 | OHLCV 캔들 API, 단위별 Endpoint, 공통 파라미터, 체결 없는 구간 처리 |
| [trades.md](./trades.md) | [페어 체결 이력 조회](https://docs.upbit.com/kr/reference/list-pair-trades) | 최근 체결 이력, `cursor`, `days_ago`, 체결 그룹 Rate Limit |
| [tickers.md](./tickers.md) | [페어 단위 현재가](https://docs.upbit.com/kr/reference/list-tickers), [마켓 단위 현재가](https://docs.upbit.com/kr/reference/list-quote-tickers) | 현재가 조회, 전일 대비 가격 변동 지표, `markets`, `quote_currencies` |
| [orderbooks.md](./orderbooks.md) | [호가 조회](https://docs.upbit.com/kr/reference/list-orderbooks), [호가 정책 조회](https://docs.upbit.com/kr/reference/list-orderbook-instruments) | 호가 스냅샷, `level`, `count`, 호가 모아보기 지원 단위 확인 |

## Endpoint 빠른 표

| API | Method | Path | 필수 파라미터 | Rate Limit 그룹 |
| --- | --- | --- | --- | --- |
| 페어 목록 조회 | GET | `/v1/market/all` | 없음 | `market` |
| 초 캔들 조회 | GET | `/v1/candles/seconds` | `market` | `candle` |
| 분 캔들 조회 | GET | `/v1/candles/minutes/{unit}` | `unit`, `market` | `candle` |
| 일 캔들 조회 | GET | `/v1/candles/days` | `market` | `candle` |
| 주 캔들 조회 | GET | `/v1/candles/weeks` | `market` | `candle` |
| 월 캔들 조회 | GET | `/v1/candles/months` | `market` | `candle` |
| 연 캔들 조회 | GET | `/v1/candles/years` | `market` | `candle` |
| 페어 체결 이력 조회 | GET | `/v1/trades/ticks` | `market` | `trade` |
| 페어 단위 현재가 조회 | GET | `/v1/ticker` | `markets` | `ticker` |
| 마켓 단위 현재가 조회 | GET | `/v1/ticker/all` | `quote_currencies` | `ticker` |
| 호가 조회 | GET | `/v1/orderbook` | `markets` | `orderbook` |
| 호가 정책 조회 | GET | `/v1/orderbook/instruments` | `markets` | `orderbook` |

Base URL:

```text
https://api.upbit.com
```

## 공통 구현 메모

- Quotation REST API는 인증 없이 호출 가능하다.
- 요청 수 제한은 IP 단위로 적용된다.
- 각 그룹은 초당 최대 10회 제한이 문서 기준 기본 정책이다.
- `Origin` 헤더가 포함된 요청은 별도 제한이 적용될 수 있으므로 서버 사이드 호출에서는 불필요한 `Origin` 헤더를 붙이지 않는다.
- 대량 또는 실시간 갱신이 필요한 현재가/체결/호가는 WebSocket 사용을 함께 검토한다.
