import { ChevronDown, Star } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

import {
  formatChangeRate,
  formatCompactKoreanAmount,
  formatKrwPrice,
  formatMarketSize,
} from "../lib/formatters";
import type { SelectedMarketSummary } from "../types";

type SelectedMarketHeaderProps = {
  market: SelectedMarketSummary;
};

export function SelectedMarketHeader({ market }: SelectedMarketHeaderProps) {
  const side = market.changeRate > 0 ? "rise" : market.changeRate < 0 ? "fall" : "flat";

  return (
    <header className="grid gap-5 border-b border-border p-5 lg:grid-cols-[minmax(280px,1fr)_auto]">
      <div className="flex min-w-0 flex-col gap-3">
        <div className="flex items-center gap-3">
          <div className="flex size-8 items-center justify-center rounded-full bg-[#f7931a] text-[15px] font-bold text-white">
            ₿
          </div>
          <div className="flex items-center gap-2">
            <h1 className="text-[22px] font-bold leading-none">
              {market.baseCurrency}
              <span className="text-[15px] font-semibold text-muted-foreground">/{market.quoteCurrency}</span>
            </h1>
            <Button variant="ghost" size="icon" aria-label="Selected Market menu">
              <ChevronDown data-icon="icon" />
            </Button>
          </div>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline" size="icon" aria-label="관심 Market">
                <Star data-icon="icon" className={market.favorite ? "fill-primary text-primary" : undefined} />
              </Button>
            </TooltipTrigger>
            <TooltipContent>관심 Market</TooltipContent>
          </Tooltip>
        </div>

        <div className="flex flex-wrap items-end gap-x-4 gap-y-2">
          <strong className="font-sans text-[40px] font-bold leading-[44px] tabular-nums text-primary">
            {formatKrwPrice(market.currentPrice)}
            <span className="ml-1 text-[15px] font-bold">KRW</span>
          </strong>
          <div className="flex items-center gap-2 pb-1">
            <Badge
              variant="secondary"
              data-side={side}
              className="data-[side=fall]:text-fall data-[side=rise]:text-rise"
            >
              {formatChangeRate(market.changeRate)}
            </Badge>
            <span
              className="text-[15px] font-semibold tabular-nums data-[side=fall]:text-fall data-[side=rise]:text-rise"
              data-side={side}
            >
              {market.changePrice > 0 ? "+" : ""}
              {formatKrwPrice(market.changePrice)}
            </span>
          </div>
        </div>
      </div>

      <dl className="grid min-w-[520px] grid-cols-2 gap-x-10 gap-y-3 text-[13px]">
        <div className="grid grid-cols-[96px_1fr] items-center gap-3">
          <dt className="text-muted-foreground">고가</dt>
          <dd className="font-semibold tabular-nums text-rise">{formatKrwPrice(market.high24h)}</dd>
        </div>
        <div className="grid grid-cols-[120px_1fr] items-center gap-3">
          <dt className="text-muted-foreground">거래량(24H)</dt>
          <dd className="font-semibold tabular-nums">
            {formatMarketSize(market.tradeVolume24h)} {market.baseCurrency}
          </dd>
        </div>
        <div className="grid grid-cols-[96px_1fr] items-center gap-3">
          <dt className="text-muted-foreground">저가</dt>
          <dd className="font-semibold tabular-nums text-fall">{formatKrwPrice(market.low24h)}</dd>
        </div>
        <div className="grid grid-cols-[120px_1fr] items-center gap-3">
          <dt className="text-muted-foreground">거래대금(24H)</dt>
          <dd className="font-semibold tabular-nums">
            {formatCompactKoreanAmount(market.tradeValue24h)}
          </dd>
        </div>
      </dl>

      <Separator className="lg:hidden" />
    </header>
  );
}
