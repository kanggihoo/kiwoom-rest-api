import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

import { formatKrwPrice, formatMarketSize } from "../lib/formatters";
import type { TradeRow } from "../types";

type RecentTradesPanelProps = {
  trades: TradeRow[];
};

export function RecentTradesPanel({ trades }: RecentTradesPanelProps) {
  return (
    <Card className="rounded-md border-border bg-card shadow-none">
      <CardHeader className="border-b border-border px-4 py-3">
        <CardTitle className="text-[17px]">체결</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="h-9 px-4 text-[12px]">시간</TableHead>
              <TableHead className="h-9 px-4 text-right text-[12px]">체결가(KRW)</TableHead>
              <TableHead className="h-9 px-4 text-right text-[12px]">수량(ETH)</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {trades.map((trade) => (
              <TableRow key={`${trade.time}-${trade.price}-${trade.size}`} className="h-8">
                <TableCell className="px-4 py-1 text-[12px] text-muted-foreground">{trade.time}</TableCell>
                <TableCell className="px-4 py-1 text-right text-[12px] font-semibold tabular-nums data-[side=fall]:text-fall data-[side=rise]:text-rise" data-side={trade.side}>
                  {formatKrwPrice(trade.price)}
                </TableCell>
                <TableCell className="px-4 py-1 text-right text-[12px] tabular-nums">
                  {formatMarketSize(trade.size)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
