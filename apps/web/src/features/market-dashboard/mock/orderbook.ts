import type { OrderbookRow } from "../types";

const askPrices = [103_506_000, 103_507_000, 103_508_000, 103_509_000, 103_510_000, 103_511_000, 103_512_000, 103_513_000];
const bidPrices = [103_505_000, 103_504_000, 103_503_000, 103_502_000, 103_501_000, 103_500_000, 103_499_000, 103_498_000];

export const mockOrderbook: OrderbookRow[] = [
  ...askPrices.map((price, index) => ({
    price,
    size: Number((0.876 + index * 0.417).toFixed(3)),
    total: Number((0.876 + index * 1.216).toFixed(3)),
    side: "ask" as const,
    depthRatio: Math.min(100, 18 + index * 9),
  })),
  ...bidPrices.map((price, index) => ({
    price,
    size: Number((0.842 + index * 0.383).toFixed(3)),
    total: Number((0.842 + index * 1.087).toFixed(3)),
    side: "bid" as const,
    depthRatio: Math.min(100, 22 + index * 8),
  })),
];
