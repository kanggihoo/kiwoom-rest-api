import type { IndexStripItem } from "../types";

export const mockIndexes: IndexStripItem[] = [
  {
    label: "KOSPI",
    value: "2,728.34",
    changeRate: 0.0041,
    side: "rise",
    sparkline: [20, 22, 21, 24, 25, 23, 27, 28, 26, 30, 31, 29],
  },
  {
    label: "KOSDAQ",
    value: "867.15",
    changeRate: -0.0032,
    side: "fall",
    sparkline: [30, 28, 29, 27, 26, 25, 27, 24, 23, 25, 22, 21],
  },
  {
    label: "USD/KRW",
    value: "1,370.50",
    changeRate: 0.0023,
    side: "rise",
    sparkline: [22, 21, 23, 22, 24, 25, 23, 24, 26, 25, 27, 26],
  },
  {
    label: "NASDAQ",
    value: "16,892.20",
    changeRate: 0.0075,
    side: "rise",
    sparkline: [15, 17, 16, 18, 21, 20, 23, 24, 22, 25, 27, 28],
  },
  {
    label: "S&P 500",
    value: "5,315.59",
    changeRate: 0.0058,
    side: "rise",
    sparkline: [18, 18, 19, 20, 21, 23, 22, 24, 25, 26, 28, 29],
  },
  {
    label: "BTC 도미넌스",
    value: "52.31%",
    changeRate: -0.0042,
    side: "fall",
    sparkline: [27, 26, 28, 25, 26, 24, 23, 22, 23, 21, 20, 19],
  },
];
