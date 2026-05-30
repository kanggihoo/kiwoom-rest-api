import type { ErrorEnvelope } from "@/lib/contracts/errors";

export type StreamType = "SNAPSHOT" | "REALTIME";

export type AskBid = "ASK" | "BID";

export type CandleUnit = "1m" | "5m" | "15m" | "30m" | "1h" | "1d" | "1w";

export type RealtimeCandleUnit = "1m" | "5m" | "15m" | "30m" | "1h";

export type AlertKind = "dailyRise" | "dailyDrop" | "shortTermRise" | "shortTermDrop";

export type Severity = "info" | "warning";

export type TickerData = {
  /** Market 코드. Upbit ticker.code 기준. */
  market: string;
  /** 시가. Upbit ticker.opening_price 기준. */
  openingPrice: number;
  /** 고가. Upbit ticker.high_price 기준. */
  highPrice: number;
  /** 저가. Upbit ticker.low_price 기준. */
  lowPrice: number;
  /** 현재가. Upbit ticker.trade_price 기준. */
  tradePrice: number;
  /** 전일 대비 가격 변동 값. Upbit ticker.signed_change_price 기준. */
  signedChangePrice: number;
  /** 전일 대비 등락률. Upbit ticker.signed_change_rate 기준. */
  signedChangeRate: number;
  /** 최근 거래량. Upbit ticker.trade_volume 기준. */
  tradeVolume: number;
  /** 최근 24시간 누적 거래량. Upbit ticker.acc_trade_volume_24h 기준. */
  accTradeVolume24h: number;
  /** 최근 24시간 누적 거래대금. Upbit ticker.acc_trade_price_24h 기준. */
  accTradePrice24h: number;
  /** 체결 타임스탬프(ms). Upbit ticker.trade_timestamp 기준. */
  tradeTimestampMs: number;
  /** Upbit 이벤트 타임스탬프(ms). Upbit ticker.timestamp 기준. */
  timestampMs: number;
  /** Upbit stream_type. */
  streamType: StreamType;
};

export type TradeData = {
  market: string;
  tradePrice: number;
  tradeVolume: number;
  askBid: AskBid;
  tradeTimestampMs: number;
  sequentialId: number;
  timestampMs: number;
  streamType: StreamType;
};

export type OrderbookUnit = {
  askPrice: number;
  bidPrice: number;
  askSize: number;
  bidSize: number;
};

export type OrderbookData = {
  market: string;
  totalAskSize: number;
  totalBidSize: number;
  level: number;
  units: OrderbookUnit[];
  timestampMs: number;
  streamType: StreamType;
};

export type Candle = {
  candleDateTimeUtc: string;
  candleDateTimeKst: string;
  openingPrice: number;
  highPrice: number;
  lowPrice: number;
  tradePrice: number;
  candleAccTradeVolume: number;
  candleAccTradePrice: number;
};

export type CandleUpdateData = {
  market: string;
  candleUnit: RealtimeCandleUnit;
  candle: Candle;
  timestampMs: number;
  streamType: StreamType;
};

export type AlertData = {
  id: string;
  market: string;
  alertKind: AlertKind;
  title: string;
  message: string;
  severity: Severity;
  basisRate: number;
  basisWindow: "24h" | "1m";
  createdAt: string;
};

export type TickerUpdateEvent = {
  type: "ticker:update";
  timestamp: string;
  data: TickerData;
};

export type TradeUpdateEvent = {
  type: "trade:update";
  timestamp: string;
  data: TradeData;
};

export type OrderbookUpdateEvent = {
  type: "orderbook:update";
  timestamp: string;
  data: OrderbookData;
};

export type CandleUpdateEvent = {
  type: "candle:update";
  timestamp: string;
  data: CandleUpdateData;
};

export type AlertNewEvent = {
  type: "alert:new";
  timestamp: string;
  data: AlertData;
};

export type BackendEvent =
  | TickerUpdateEvent
  | TradeUpdateEvent
  | OrderbookUpdateEvent
  | CandleUpdateEvent
  | AlertNewEvent;

export type RealtimeMessage = BackendEvent | ErrorEnvelope;
