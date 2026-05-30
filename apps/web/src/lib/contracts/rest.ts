import type { Candle, CandleUnit, TickerData } from "./events";

export type RestEnvelope<TType extends string, TData> = {
  type: TType;
  timestamp: string;
  data: TData;
};

export type MarketSummary = {
  market: string;
  koreanName: string;
  englishName: string;
  quoteCurrency: string;
  baseCurrency: string;
};

export type MarketsListResponse = RestEnvelope<
  "markets:list",
  {
    markets: MarketSummary[];
  }
>;

export type MarketStateSnapshotResponse = RestEnvelope<
  "market-state:snapshot",
  {
    generatedAt: string;
    tickers: TickerData[];
  }
>;

export type CandlesListResponse = RestEnvelope<
  "candles:list",
  {
    market: string;
    candleUnit: CandleUnit;
    candles: Candle[];
  }
>;

export type RestSuccessResponse =
  | MarketsListResponse
  | MarketStateSnapshotResponse
  | CandlesListResponse;
