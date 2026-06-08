import { Info } from "lucide-react";

import { Card } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

import type { CandlePoint, CandleUnit, SelectedMarketSummary } from "../types";
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
    <Card className="flex h-full min-h-[680px] flex-col overflow-hidden rounded-md border-border bg-card p-0 shadow-none">
      <SelectedMarketHeader market={market} />
      <div className="flex min-h-[52px] items-center justify-between gap-4 border-b border-border px-5">
        <Tabs value={activeCandleUnit}>
          <TabsList className="h-[52px] gap-6 bg-transparent p-0">
            <TabsTrigger
              value="1d"
              className="h-[52px] rounded-none border-b-2 border-transparent px-0 data-[active=true]:border-primary data-[active=true]:bg-transparent data-[active=true]:text-primary"
            >
              1일
            </TabsTrigger>
            <TabsTrigger
              value="1w"
              className="h-[52px] rounded-none border-b-2 border-transparent px-0 data-[active=true]:border-primary data-[active=true]:bg-transparent data-[active=true]:text-primary"
            >
              1주
            </TabsTrigger>
            <TabsTrigger
              value="1m"
              className="h-[52px] rounded-none border-b-2 border-transparent px-0 data-[active=true]:border-primary data-[active=true]:bg-transparent data-[active=true]:text-primary"
            >
              1개월
            </TabsTrigger>
            <TabsTrigger
              value="5m"
              className="h-[52px] rounded-none border-b-2 border-transparent px-0 data-[active=true]:border-primary data-[active=true]:bg-transparent data-[active=true]:text-primary"
            >
              3개월
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>
      <div className="min-h-0 flex-1">
        <LightweightCandleChart candles={candles} />
      </div>
      <div className="border-t border-border px-5 py-3">
        <div className="flex flex-wrap items-center justify-between gap-3 text-[12px] font-semibold text-muted-foreground">
          <div className="flex items-center gap-2">
            <span>차트 데이터는 참고용으로 실제와 다를 수 있습니다.</span>
            <span>기준: 2025-06-02 16:45:12 (KST)</span>
          </div>
          <div className="flex items-center gap-5 text-foreground">
            <span className="flex items-center gap-1">
              지표 없음
              <Info data-icon="inline-end" />
            </span>
            <span>%</span>
            <span>로그</span>
            <span>UTC+9</span>
          </div>
        </div>
      </div>
    </Card>
  );
}
