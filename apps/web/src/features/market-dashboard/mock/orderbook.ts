import type { OrderbookRow } from "../types";

const askPrices = [2_904_000, 2_905_000, 2_906_000, 2_907_000, 2_908_000, 2_909_000, 2_910_000, 2_911_000];
const bidPrices = [2_903_000, 2_902_000, 2_901_000, 2_900_000, 2_899_000, 2_898_000, 2_897_000, 2_896_000];

export const mockOrderbook: OrderbookRow[] = [
  ...askPrices.map((price, index) => ({
    price,
    size: Number((8.76 + index * 4.17).toFixed(3)),
    total: Number((8.76 + index * 12.16).toFixed(3)),
    side: "ask" as const,
    depthRatio: Math.min(100, 18 + index * 9),
  })),
  ...bidPrices.map((price, index) => ({
    price,
    size: Number((8.42 + index * 3.83).toFixed(3)),
    total: Number((8.42 + index * 10.87).toFixed(3)),
    side: "bid" as const,
    depthRatio: Math.min(100, 22 + index * 8),
  })),
];
