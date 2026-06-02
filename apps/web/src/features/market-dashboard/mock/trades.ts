import type { TradeRow } from "../types";

export const mockTrades: TradeRow[] = [
  { time: "09:41:23", price: 103_500_000, size: 0.0312, side: "rise" },
  { time: "09:41:22", price: 103_501_000, size: 0.052, side: "rise" },
  { time: "09:41:21", price: 103_500_000, size: 0.0105, side: "rise" },
  { time: "09:41:20", price: 103_499_000, size: 0.025, side: "fall" },
  { time: "09:41:19", price: 103_500_000, size: 0.002, side: "rise" },
  { time: "09:41:18", price: 103_501_000, size: 0.113, side: "rise" },
  { time: "09:41:17", price: 103_500_000, size: 0.045, side: "rise" },
  { time: "09:41:16", price: 103_501_000, size: 0.008, side: "rise" },
  { time: "09:41:15", price: 103_500_000, size: 0.1201, side: "rise" },
  { time: "09:41:14", price: 103_499_000, size: 0.03, side: "fall" },
];
