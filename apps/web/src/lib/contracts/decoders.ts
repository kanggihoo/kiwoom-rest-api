import type { ErrorEnvelope } from "@/lib/contracts/errors";
import type {
  AlertData,
  AlertNewEvent,
  BackendEvent,
  Candle,
  CandleUpdateData,
  CandleUpdateEvent,
  OrderbookData,
  OrderbookUpdateEvent,
  AskBid,
  StreamType,
  TickerData,
  TickerUpdateEvent,
  TradeData,
  TradeUpdateEvent,
} from "@/lib/contracts/events";
import type {
  CandlesListResponse,
  MarketStateSnapshotResponse,
  MarketsListResponse,
  MarketSummary,
  RestSuccessResponse,
} from "@/lib/contracts/rest";

type UnknownRecord = Record<string, unknown>;

const isRecord = (value: unknown): value is UnknownRecord =>
  typeof value === "object" && value !== null && !Array.isArray(value);

const isString = (value: unknown): value is string => typeof value === "string";
const isNumber = (value: unknown): value is number =>
  typeof value === "number" && Number.isFinite(value);
const isStringEnum = (value: unknown, values: readonly string[]): value is string =>
  isString(value) && values.includes(value);
const isArray = (value: unknown): value is unknown[] => Array.isArray(value);

const isStreamType = (value: unknown): value is StreamType =>
  isStringEnum(value, ["SNAPSHOT", "REALTIME"]);

const isAskBid = (value: unknown): value is AskBid => isStringEnum(value, ["ASK", "BID"]);

const isCandle = (value: unknown): value is Candle =>
  isRecord(value) &&
  isString(value.candleDateTimeUtc) &&
  isString(value.candleDateTimeKst) &&
  isNumber(value.openingPrice) &&
  isNumber(value.highPrice) &&
  isNumber(value.lowPrice) &&
  isNumber(value.tradePrice) &&
  isNumber(value.candleAccTradeVolume) &&
  isNumber(value.candleAccTradePrice);

const isTickerData = (value: unknown): value is TickerData =>
  isRecord(value) &&
  isString(value.market) &&
  isNumber(value.openingPrice) &&
  isNumber(value.highPrice) &&
  isNumber(value.lowPrice) &&
  isNumber(value.tradePrice) &&
  isNumber(value.signedChangePrice) &&
  isNumber(value.signedChangeRate) &&
  isNumber(value.tradeVolume) &&
  isNumber(value.accTradeVolume24h) &&
  isNumber(value.accTradePrice24h) &&
  isNumber(value.tradeTimestampMs) &&
  isNumber(value.timestampMs) &&
  isStreamType(value.streamType);

const isTradeData = (value: unknown): value is TradeData =>
  isRecord(value) &&
  isString(value.market) &&
  isNumber(value.tradePrice) &&
  isNumber(value.tradeVolume) &&
  isAskBid(value.askBid) &&
  isNumber(value.tradeTimestampMs) &&
  isNumber(value.sequentialId) &&
  isNumber(value.timestampMs) &&
  isStreamType(value.streamType);

const isOrderbookUnit = (value: unknown): value is {
  askPrice: number;
  bidPrice: number;
  askSize: number;
  bidSize: number;
} =>
  isRecord(value) &&
  isNumber(value.askPrice) &&
  isNumber(value.bidPrice) &&
  isNumber(value.askSize) &&
  isNumber(value.bidSize);

const isOrderbookData = (value: unknown): value is OrderbookData =>
  isRecord(value) &&
  isString(value.market) &&
  isNumber(value.totalAskSize) &&
  isNumber(value.totalBidSize) &&
  isNumber(value.level) &&
  isArray(value.units) &&
  value.units.every(isOrderbookUnit) &&
  isNumber(value.timestampMs) &&
  isStreamType(value.streamType);

const isCandleUpdateData = (value: unknown): value is CandleUpdateData =>
  isRecord(value) &&
  isString(value.market) &&
  isStringEnum(value.candleUnit, ["1m", "5m", "15m", "30m", "1h"]) &&
  isCandle(value.candle) &&
  isNumber(value.timestampMs) &&
  isStreamType(value.streamType);

const isAlertKind = (value: unknown): value is AlertData["alertKind"] =>
  isStringEnum(value, ["dailyRise", "dailyDrop", "shortTermRise", "shortTermDrop"]);
const isSeverity = (value: unknown): value is AlertData["severity"] =>
  isStringEnum(value, ["info", "warning"]);

const isAlertData = (value: unknown): value is AlertData =>
  isRecord(value) &&
  isString(value.id) &&
  isString(value.market) &&
  isAlertKind(value.alertKind) &&
  isString(value.title) &&
  isString(value.message) &&
  isSeverity(value.severity) &&
  isNumber(value.basisRate) &&
  isStringEnum(value.basisWindow, ["24h", "1m"]) &&
  isString(value.createdAt);

const isTickerUpdateEvent = (value: unknown): value is TickerUpdateEvent =>
  isRecord(value) &&
  value.type === "ticker:update" &&
  isString(value.timestamp) &&
  isTickerData(value.data);

const isTradeUpdateEvent = (value: unknown): value is TradeUpdateEvent =>
  isRecord(value) &&
  value.type === "trade:update" &&
  isString(value.timestamp) &&
  isTradeData(value.data);

const isOrderbookUpdateEvent = (value: unknown): value is OrderbookUpdateEvent =>
  isRecord(value) &&
  value.type === "orderbook:update" &&
  isString(value.timestamp) &&
  isOrderbookData(value.data);

const isCandleUpdateEvent = (value: unknown): value is CandleUpdateEvent =>
  isRecord(value) &&
  value.type === "candle:update" &&
  isString(value.timestamp) &&
  isCandleUpdateData(value.data);

const isAlertNewEvent = (value: unknown): value is AlertNewEvent =>
  isRecord(value) &&
  value.type === "alert:new" &&
  isString(value.timestamp) &&
  isAlertData(value.data);

const isMarketSummary = (value: unknown): value is MarketSummary =>
  isRecord(value) &&
  isString(value.market) &&
  isString(value.koreanName) &&
  isString(value.englishName) &&
  isString(value.quoteCurrency) &&
  isString(value.baseCurrency);

const isMarketsList = (value: unknown): value is MarketsListResponse =>
  isRecord(value) &&
  value.type === "markets:list" &&
  isString(value.timestamp) &&
  isRecord(value.data) &&
  isArray(value.data.markets) &&
  value.data.markets.every(isMarketSummary);

const isMarketStateSnapshot = (value: unknown): value is MarketStateSnapshotResponse =>
  isRecord(value) &&
  value.type === "market-state:snapshot" &&
  isString(value.timestamp) &&
  isRecord(value.data) &&
  isString(value.data.generatedAt) &&
  isArray(value.data.tickers) &&
  value.data.tickers.every(isTickerData);

const isCandlesList = (value: unknown): value is CandlesListResponse =>
  isRecord(value) &&
  value.type === "candles:list" &&
  isString(value.timestamp) &&
  isRecord(value.data) &&
  isString(value.data.market) &&
  isStringEnum(value.data.candleUnit, ["1m", "5m", "15m", "30m", "1h", "1d", "1w"]) &&
  isArray(value.data.candles) &&
  value.data.candles.every(isCandle);

export const isBackendEvent = (value: unknown): value is BackendEvent =>
  isTickerUpdateEvent(value) ||
  isTradeUpdateEvent(value) ||
  isOrderbookUpdateEvent(value) ||
  isCandleUpdateEvent(value) ||
  isAlertNewEvent(value);

export const isErrorEnvelope = (value: unknown): value is ErrorEnvelope =>
  isRecord(value) &&
  value.type === "error" &&
  isString(value.timestamp) &&
  isRecord(value.data) &&
  isString(value.data.code) &&
  isString(value.data.message);

export const parseBackendEvent = (value: unknown): BackendEvent => {
  if (!isBackendEvent(value)) {
    throw new Error("Invalid backend realtime event shape.");
  }
  return value;
};

export const parseRealtimeMessage = (value: unknown): BackendEvent | ErrorEnvelope => {
  if (isBackendEvent(value) || isErrorEnvelope(value)) {
    return value;
  }
  throw new Error("Invalid realtime message shape.");
};

export const isRestSuccessResponse = (value: unknown): value is RestSuccessResponse =>
  isMarketsList(value) || isMarketStateSnapshot(value) || isCandlesList(value);

export const parseRestResponse = (value: unknown): RestSuccessResponse => {
  if (!isRestSuccessResponse(value)) {
    throw new Error("Invalid REST success payload shape.");
  }
  return value;
};

export const assertType = <T>(value: unknown, guard: (candidate: unknown) => candidate is T): T => {
  if (!guard(value)) {
    throw new Error("Invalid payload shape.");
  }
  return value;
};
