import type { CandlePoint } from "../types";

const start = Math.floor(Date.UTC(2026, 5, 2, 0, 0, 0) / 1000);

export const mockCandles: CandlePoint[] = Array.from({ length: 96 }, (_, index) => {
  const wave = Math.sin(index / 6) * 1_800_000;
  const drift = index * 42_000;
  const base = 100_800_000 + wave + drift;
  const open = Math.round(base + Math.sin(index) * 420_000);
  const close = Math.round(base + Math.cos(index / 2) * 520_000);
  const high = Math.max(open, close) + 430_000 + (index % 5) * 52_000;
  const low = Math.min(open, close) - 390_000 - (index % 4) * 48_000;

  return {
    time: start + index * 3600,
    open,
    high,
    low,
    close,
    volume: 120 + (index % 12) * 18 + Math.abs(Math.sin(index / 4)) * 140,
  };
});
