import { ChevronDown, Search, SlidersHorizontal, Star } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";

import {
  formatChangeRate,
  formatCompactKoreanAmount,
  formatKrwPrice,
  formatMarketVolume,
} from "../lib/formatters";
import type { MarketRow } from "../types";
import { Sparkline } from "./sparkline";

type MarketTablePanelProps = {
  markets: MarketRow[];
};

export function MarketTablePanel({ markets }: MarketTablePanelProps) {
  return (
    <Card className="flex h-full min-h-[680px] flex-col overflow-hidden rounded-md border-border bg-card shadow-none">
      <CardHeader className="border-b border-border px-4 py-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <h2 className="text-[17px] font-bold leading-[23px]">실시간 마켓</h2>
            <span className="text-[13px] font-semibold tabular-nums text-muted-foreground">16:45:12</span>
            <Badge variant="secondary" className="rounded-md bg-emerald-50 text-emerald-700">
              실시간 연결됨
            </Badge>
          </div>
          <div className="flex items-center gap-2">
            <InputGroup className="h-9 w-[190px] rounded-md bg-muted">
              <InputGroupAddon>
                <Search data-icon="inline-start" />
              </InputGroupAddon>
              <InputGroupInput placeholder="마켓 검색" aria-label="Market table search" />
            </InputGroup>
            <Button variant="outline" size="icon" aria-label="Market filter">
              <SlidersHorizontal data-icon="icon" />
            </Button>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3">
          <Tabs value="all">
            <TabsList className="h-9 gap-1 bg-transparent p-0">
              <TabsTrigger value="all" className="h-9 px-4">
                전체
              </TabsTrigger>
              <TabsTrigger value="KRW" className="h-9 px-4">
                KRW
              </TabsTrigger>
              <TabsTrigger value="BTC" className="h-9 px-4">
                BTC
              </TabsTrigger>
            </TabsList>
          </Tabs>
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm" className="gap-1">
              거래대금
              <ChevronDown data-icon="inline-end" />
            </Button>
            <Button variant="secondary" size="sm">
              상승률
            </Button>
            <Button variant="secondary" size="sm">
              하락률
            </Button>
            <Button variant="secondary" size="sm">
              관심
            </Button>
            <Button variant="secondary" size="sm">
              실시간
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="min-h-0 flex-1 p-0">
        <ScrollArea className="h-full">
          <Table className="table-fixed">
            <TableHeader className="sticky top-0 z-[1] bg-card">
              <TableRow className="hover:bg-transparent">
                <TableHead className="h-10 w-[34px] px-2">
                  <Star data-icon="icon" className="text-muted-foreground" />
                </TableHead>
                <TableHead className="h-10 w-[90px] px-1.5 text-[11px]">마켓</TableHead>
                <TableHead className="h-10 w-[64px] px-1.5 text-[11px]">한글명</TableHead>
                <TableHead className="h-10 w-[94px] px-1.5 text-right text-[11px]">현재가</TableHead>
                <TableHead className="h-10 w-[76px] px-1.5 text-right text-[11px]">등락률(24H)</TableHead>
                <TableHead className="h-10 w-[84px] px-1.5 text-right text-[11px]">거래대금(24H)</TableHead>
                <TableHead className="h-10 w-[86px] px-1.5 text-right text-[11px]">거래량(24H)</TableHead>
                <TableHead className="h-10 w-[86px] px-1.5 text-right text-[11px]">고가(24H)</TableHead>
                <TableHead className="h-10 w-[86px] px-1.5 text-right text-[11px]">저가(24H)</TableHead>
                <TableHead className="h-10 w-[52px] px-1.5 text-right text-[11px]">24H</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {markets.map((market) => {
                const side = market.changeRate > 0 ? "rise" : market.changeRate < 0 ? "fall" : "flat";

                return (
                  <TableRow
                    key={market.market}
                    className={cn("h-[54px]", market.selected && "bg-accent/80 hover:bg-accent")}
                  >
                    <TableCell className="px-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="size-7 rounded-[8px]"
                        aria-label={`${market.market} 관심`}
                      >
                        <Star
                          data-icon="icon"
                          className={market.favorite ? "fill-amber-400 text-amber-400" : "text-muted-foreground"}
                        />
                      </Button>
                    </TableCell>
                    <TableCell className="px-1.5">
                      <span className="block truncate text-[13px] font-bold tabular-nums">{market.market}</span>
                    </TableCell>
                    <TableCell className="px-1.5">
                      <span className="block truncate text-[12px] font-semibold text-muted-foreground">
                        {market.koreanName}
                      </span>
                    </TableCell>
                    <TableCell className="truncate px-1.5 text-right text-[12px] font-bold tabular-nums">
                      {formatKrwPrice(market.currentPrice)}
                    </TableCell>
                    <TableCell
                      className="truncate px-1.5 text-right text-[12px] font-semibold tabular-nums data-[side=fall]:text-fall data-[side=rise]:text-rise"
                      data-side={side}
                    >
                      {formatChangeRate(market.changeRate)}
                    </TableCell>
                    <TableCell className="truncate px-1.5 text-right text-[12px] font-semibold tabular-nums">
                      {formatCompactKoreanAmount(market.tradeValue24h)}
                    </TableCell>
                    <TableCell className="truncate px-1.5 text-right text-[12px] tabular-nums">
                      {formatMarketVolume(market.tradeVolume24h)}
                    </TableCell>
                    <TableCell className="truncate px-1.5 text-right text-[11px] font-semibold tabular-nums text-rise">
                      {formatKrwPrice(market.highPrice)}
                    </TableCell>
                    <TableCell className="truncate px-1.5 text-right text-[11px] font-semibold tabular-nums text-fall">
                      {formatKrwPrice(market.lowPrice)}
                    </TableCell>
                    <TableCell className="px-1.5">
                      <div className="flex justify-end">
                        <Sparkline
                          values={market.sparkline}
                          className="h-6 w-[46px]"
                          variant={side === "rise" ? "rise" : side === "fall" ? "fall" : "muted"}
                        />
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </ScrollArea>
      </CardContent>

      <div className="border-t border-border px-4 py-3 text-[13px] font-semibold text-muted-foreground">
        293개 마켓 · 스크롤로 더 보기
      </div>
    </Card>
  );
}
