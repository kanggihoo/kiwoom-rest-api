import { MoreHorizontal, Star } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

import {
  formatChangeRate,
  formatCompactKoreanAmount,
  formatKrwPrice,
  formatMarketVolume,
} from "../lib/formatters";
import type { SelectedMarketSummary } from "../types";

type SelectedMarketHeaderProps = {
  market: SelectedMarketSummary;
};

export function SelectedMarketHeader({ market }: SelectedMarketHeaderProps) {
  const side = market.changeRate > 0 ? "rise" : market.changeRate < 0 ? "fall" : "flat";

  return (
    <header className="border-b border-border px-5 pb-4 pt-5">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <h1 className="text-[18px] font-extrabold leading-[23px]">
            {market.market} 일봉
          </h1>
          <strong
            className="mt-3 block font-sans text-[40px] font-bold leading-[44px] tabular-nums data-[side=fall]:text-fall data-[side=rise]:text-rise"
            data-side={side}
          >
            {formatKrwPrice(market.currentPrice)}
          </strong>
          <div
            className="mt-1 flex items-center gap-2 text-[16px] font-semibold tabular-nums data-[side=fall]:text-fall data-[side=rise]:text-rise"
            data-side={side}
          >
            <span>{formatChangeRate(market.changeRate)}</span>
            <span>
              ({market.changePrice > 0 ? "+" : ""}
              {formatKrwPrice(market.changePrice)})
            </span>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" aria-label="관심 Market">
                <Star data-icon="icon" className={market.favorite ? "fill-amber-400 text-amber-400" : undefined} />
              </Button>
            </TooltipTrigger>
            <TooltipContent>관심 Market</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" aria-label="차트 옵션">
                <MoreHorizontal data-icon="icon" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>차트 옵션</TooltipContent>
          </Tooltip>
        </div>
      </div>

      <dl className="mt-5 grid grid-cols-3 divide-x divide-border text-[13px]">
        <div className="flex flex-col gap-2 pr-4">
          <dt className="text-muted-foreground">고가(24H)</dt>
          <dd className="font-bold tabular-nums text-rise">{formatKrwPrice(market.high24h)}</dd>
        </div>
        <div className="flex flex-col gap-2 px-4">
          <dt className="text-muted-foreground">거래대금(24H)</dt>
          <dd className="font-bold tabular-nums">{formatCompactKoreanAmount(market.tradeValue24h)}</dd>
        </div>
        <div className="flex flex-col gap-2 pl-4">
          <dt className="text-muted-foreground">거래량(24H)</dt>
          <dd className="font-bold tabular-nums">
            {formatMarketVolume(market.tradeVolume24h)}
          </dd>
        </div>
      </dl>
    </header>
  );
}
