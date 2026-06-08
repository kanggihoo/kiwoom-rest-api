import type { CandlePoint } from "../types";

const start = Math.floor(Date.UTC(2025, 3, 15, 0, 0, 0) / 1000);
const candleCount = 54;

export const mockCandles: CandlePoint[] = Array.from({ length: candleCount }, (_, index) => {
  const progress = index / (candleCount - 1);
  const trend = progress < 0.58 ? progress * 820_000 : 820_000 - (progress - 0.58) * 580_000;
  const wave = Math.sin(index / 2.6) * 86_000 + Math.sin(index / 6.4) * 58_000;
  const base = 2_390_000 + trend + wave;
  const open = Math.round(base + Math.sin(index * 1.35) * 42_000);
  const close = Math.round(base + Math.cos(index * 0.9) * 58_000);
  const high = Math.max(open, close) + 42_000 + (index % 5) * 9_500;
  const low = Math.min(open, close) - 38_000 - (index % 4) * 10_000;

  return {
    time: start + index * 86400,
    open,
    high,
    low,
    close,
    volume: 18_000 + (index % 12) * 2_400 + Math.abs(Math.sin(index / 3.5)) * 24_000,
  };
});
