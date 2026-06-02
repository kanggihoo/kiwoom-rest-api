import { MoreHorizontal, Plus, Star } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

import {
  formatChangeRate,
  formatCompactKoreanAmount,
  formatKrwPrice,
} from "../lib/formatters";
import type { MarketCategory, MarketRow } from "../types";

const categories: Array<{ value: MarketCategory; label: string }> = [
  { value: "interest", label: "관심" },
  { value: "KRW", label: "KRW" },
  { value: "BTC", label: "BTC" },
  { value: "USDT", label: "USDT" },
  { value: "holding", label: "보유" },
];

type MarketDiscoveryPanelProps = {
  markets: MarketRow[];
  activeCategory: MarketCategory;
};

export function MarketDiscoveryPanel({ markets, activeCategory }: MarketDiscoveryPanelProps) {
  return (
    <Card className="flex h-[calc(100vh-148px)] min-h-[640px] flex-col overflow-hidden rounded-md border-border bg-card p-0 shadow-none">
      <div className="flex h-14 items-center justify-between border-b border-border px-4">
        <Tabs value={activeCategory}>
          <TabsList className="h-10 bg-transparent p-0">
            {categories.map((category) => (
              <TabsTrigger key={category.value} value={category.value} className="h-10 px-4">
                {category.label}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
        <div className="flex items-center gap-1">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" aria-label="Market 추가">
                <Plus data-icon="icon" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Market 추가</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" aria-label="Market list 옵션">
                <MoreHorizontal data-icon="icon" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Market list 옵션</TooltipContent>
          </Tooltip>
        </div>
      </div>

      <div className="grid grid-cols-[40px_minmax(110px,1fr)_96px_78px_104px] border-b border-border px-4 py-2 text-[12px] font-semibold text-muted-foreground">
        <span />
        <span>Market</span>
        <span className="text-right">현재가</span>
        <span className="text-right">전일대비</span>
        <span className="text-right">거래대금(24H)</span>
      </div>

      <ScrollArea className="min-h-0 flex-1">
        <div className="flex flex-col">
          {markets.map((market) => {
            const side = market.changeRate > 0 ? "rise" : market.changeRate < 0 ? "fall" : "flat";

            return (
              <div
                key={market.market}
                className={cn(
                  "grid min-h-14 grid-cols-[40px_minmax(110px,1fr)_96px_78px_104px] items-center border-b border-border px-4 text-[13px]",
                  market.selected && "bg-accent",
                )}
              >
                <Button variant="ghost" size="icon" aria-label={`${market.market} 관심`}>
                  <Star
                    data-icon="icon"
                    className={market.favorite ? "fill-primary text-primary" : "text-muted-foreground"}
                  />
                </Button>
                <div className="min-w-0">
                  <div className="truncate font-bold">{market.market}</div>
                  <div className="truncate text-[12px] font-medium text-muted-foreground">{market.koreanName}</div>
                </div>
                <div className="text-right font-bold tabular-nums text-primary">
                  {formatKrwPrice(market.currentPrice)}
                </div>
                <div
                  className="text-right font-semibold tabular-nums data-[side=fall]:text-fall data-[side=rise]:text-rise"
                  data-side={side}
                >
                  {formatChangeRate(market.changeRate)}
                </div>
                <div className="text-right text-[12px] font-semibold tabular-nums">
                  {formatCompactKoreanAmount(market.tradeValue24h)}
                </div>
              </div>
            );
          })}
        </div>
      </ScrollArea>
      <div className="border-t border-border px-4 py-3">
        <Badge variant="secondary">Mock Market List</Badge>
      </div>
    </Card>
  );
}
