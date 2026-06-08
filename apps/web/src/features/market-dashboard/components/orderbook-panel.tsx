import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import { formatKrwPrice, formatMarketSize } from "../lib/formatters";
import type { OrderbookRow } from "../types";

type OrderbookPanelProps = {
  rows: OrderbookRow[];
};

export function OrderbookPanel({ rows }: OrderbookPanelProps) {
  return (
    <Card className="rounded-md border-border bg-card shadow-none">
      <CardHeader className="border-b border-border px-4 py-3">
        <CardTitle className="text-[17px]">호가</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-0 p-0">
        <div className="border-r border-border">
          <div className="grid grid-cols-3 px-4 py-2 text-[12px] font-semibold text-muted-foreground">
            <span>수량(ETH)</span>
            <span className="text-right">매수호가</span>
            <span className="text-right">누적</span>
          </div>
          {rows
            .filter((row) => row.side === "bid")
            .map((row) => (
              <div key={`${row.side}-${row.price}`} className="relative grid h-8 grid-cols-3 items-center px-4 text-[12px]">
                <div
                  className="absolute inset-y-0 right-0 bg-fall/10"
                  style={{ width: `${row.depthRatio}%` }}
                />
                <span className="relative tabular-nums">{formatMarketSize(row.size)}</span>
                <span className="relative text-right font-semibold tabular-nums text-fall">
                  {formatKrwPrice(row.price)}
                </span>
                <span className="relative text-right tabular-nums text-muted-foreground">
                  {formatMarketSize(row.total)}
                </span>
              </div>
            ))}
        </div>
        <div>
          <div className="grid grid-cols-3 px-4 py-2 text-[12px] font-semibold text-muted-foreground">
            <span className="text-right">누적</span>
            <span className="text-right">매도호가</span>
            <span className="text-right">수량(ETH)</span>
          </div>
          {rows
            .filter((row) => row.side === "ask")
            .map((row) => (
              <div key={`${row.side}-${row.price}`} className="relative grid h-8 grid-cols-3 items-center px-4 text-[12px]">
                <div
                  className="absolute inset-y-0 left-0 bg-rise/10"
                  style={{ width: `${row.depthRatio}%` }}
                />
                <span className="relative text-right tabular-nums text-muted-foreground">
                  {formatMarketSize(row.total)}
                </span>
                <span className="relative text-right font-semibold tabular-nums text-rise">
                  {formatKrwPrice(row.price)}
                </span>
                <span className="relative text-right tabular-nums">{formatMarketSize(row.size)}</span>
              </div>
            ))}
        </div>
      </CardContent>
    </Card>
  );
}
