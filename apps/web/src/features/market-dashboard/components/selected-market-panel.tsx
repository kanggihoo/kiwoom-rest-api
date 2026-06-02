import { Activity, SlidersHorizontal } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

import type { CandlePoint, CandleUnit, SelectedMarketSummary } from "../types";
import { CandleUnitToggle } from "./candle-unit-toggle";
import { LightweightCandleChart } from "./lightweight-candle-chart";
import { SelectedMarketHeader } from "./selected-market-header";

type SelectedMarketPanelProps = {
  market: SelectedMarketSummary;
  candles: CandlePoint[];
  activeCandleUnit: CandleUnit;
};

export function SelectedMarketPanel({
  market,
  candles,
  activeCandleUnit,
}: SelectedMarketPanelProps) {
  return (
    <Card className="overflow-hidden rounded-md border-border bg-card p-0 shadow-none">
      <SelectedMarketHeader market={market} />
      <div className="flex min-h-[48px] items-center justify-between gap-4 px-5">
        <CandleUnitToggle value={activeCandleUnit} />
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm">
            <Activity data-icon="inline-start" />
            기본차트
          </Button>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" aria-label="차트 지표">
                <SlidersHorizontal data-icon="icon" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>차트 지표</TooltipContent>
          </Tooltip>
        </div>
      </div>
      <LightweightCandleChart candles={candles} />
    </Card>
  );
}
