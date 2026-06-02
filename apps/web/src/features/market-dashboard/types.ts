export type MovementSide = "rise" | "fall" | "flat";

export type MarketCategory = "interest" | "KRW" | "BTC" | "USDT" | "holding";

export type CandleUnit = "1m" | "5m" | "15m" | "1h" | "1d" | "1w";

export type IndexStripItem = {
  label: string;
  value: string;
  changeRate: number;
  side: MovementSide;
  sparkline: number[];
};

export type MarketRow = {
  market: string;
  koreanName: string;
  englishName: string;
  baseCurrency: string;
  quoteCurrency: string;
  currentPrice: number;
  changeRate: number;
  changePrice: number;
  tradeVolume24h: number;
  tradeValue24h: number;
  openPrice: number;
  highPrice: number;
  lowPrice: number;
  favorite: boolean;
  selected: boolean;
  sparkline: number[];
};

export type SelectedMarketSummary = MarketRow & {
  high24h: number;
  low24h: number;
};

export type CandlePoint = {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

export type OrderbookRow = {
  price: number;
  size: number;
  total: number;
  side: "ask" | "bid";
  depthRatio: number;
};

export type TradeRow = {
  time: string;
  price: number;
  size: number;
  side: "rise" | "fall";
};

export type MarketDashboardMockData = {
  selectedMarket: SelectedMarketSummary;
  activeCandleUnit: CandleUnit;
  activeCategory: MarketCategory;
  indexes: IndexStripItem[];
  markets: MarketRow[];
  candles: CandlePoint[];
  orderbook: OrderbookRow[];
  trades: TradeRow[];
};
