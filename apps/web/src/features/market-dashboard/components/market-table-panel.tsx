import { Search, Star } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

import {
  formatChangeRate,
  formatCompactKoreanAmount,
  formatKrwPrice,
  formatMarketSize,
} from "../lib/formatters";
import type { MarketRow } from "../types";
import { Sparkline } from "./sparkline";

type MarketTablePanelProps = {
  markets: MarketRow[];
};

export function MarketTablePanel({ markets }: MarketTablePanelProps) {
  return (
    <Card className="rounded-md border-border bg-card shadow-none">
      <CardHeader className="flex-row items-center justify-between border-b border-border px-4 py-3">
        <Tabs value="all">
          <TabsList className="h-9 bg-transparent p-0">
            <TabsTrigger value="all">전체</TabsTrigger>
            <TabsTrigger value="KRW">KRW</TabsTrigger>
            <TabsTrigger value="BTC">BTC</TabsTrigger>
            <TabsTrigger value="USDT">USDT</TabsTrigger>
            <TabsTrigger value="holding">보유</TabsTrigger>
            <TabsTrigger value="interest">관심</TabsTrigger>
          </TabsList>
        </Tabs>
        <div className="flex items-center gap-2">
          <Select value="all">
            <SelectTrigger className="h-9 w-[140px]">
              <SelectValue placeholder="전체 Market" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">전체 Market</SelectItem>
              <SelectItem value="krw">KRW Market</SelectItem>
              <SelectItem value="favorites">관심 Market</SelectItem>
            </SelectContent>
          </Select>
          <InputGroup className="h-9 w-[220px] bg-muted">
            <InputGroupAddon>
              <Search data-icon="inline-start" />
            </InputGroupAddon>
            <InputGroupInput placeholder="Market 검색" aria-label="Market table search" />
          </InputGroup>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[220px] px-4">Market</TableHead>
              <TableHead className="text-right">현재가</TableHead>
              <TableHead className="text-right">전일대비</TableHead>
              <TableHead className="text-right">거래량(24H)</TableHead>
              <TableHead className="text-right">거래대금(24H)</TableHead>
              <TableHead className="text-right">시가</TableHead>
              <TableHead className="text-right">고가</TableHead>
              <TableHead className="text-right">저가</TableHead>
              <TableHead className="w-[110px] text-right">차트(1일)</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {markets.map((market) => {
              const side = market.changeRate > 0 ? "rise" : market.changeRate < 0 ? "fall" : "flat";

              return (
                <TableRow key={market.market} className="h-[56px]">
                  <TableCell className="px-4">
                    <div className="flex items-center gap-3">
                      <Button variant="ghost" size="icon" aria-label={`${market.market} 관심`}>
                        <Star
                          data-icon="icon"
                          className={market.favorite ? "fill-primary text-primary" : "text-muted-foreground"}
                        />
                      </Button>
                      <div className="min-w-0">
                        <div className="truncate font-bold">{market.market}</div>
                        <div className="truncate text-[12px] text-muted-foreground">{market.koreanName}</div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="text-right font-bold tabular-nums text-primary">
                    {formatKrwPrice(market.currentPrice)}
                  </TableCell>
                  <TableCell className="text-right font-semibold tabular-nums data-[side=fall]:text-fall data-[side=rise]:text-rise" data-side={side}>
                    {formatChangeRate(market.changeRate)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">{formatMarketSize(market.tradeVolume24h)}</TableCell>
                  <TableCell className="text-right tabular-nums">{formatCompactKoreanAmount(market.tradeValue24h)}</TableCell>
                  <TableCell className="text-right tabular-nums text-rise">{formatKrwPrice(market.openPrice)}</TableCell>
                  <TableCell className="text-right tabular-nums text-rise">{formatKrwPrice(market.highPrice)}</TableCell>
                  <TableCell className="text-right tabular-nums text-fall">{formatKrwPrice(market.lowPrice)}</TableCell>
                  <TableCell className="pr-4">
                    <div className="flex justify-end">
                      <Sparkline
                        values={market.sparkline}
                        variant={side === "rise" ? "rise" : side === "fall" ? "fall" : "muted"}
                      />
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
