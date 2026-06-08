import {
  ArrowDown,
  ArrowUp,
  CalendarClock,
  ChevronDown,
  Flame,
  Moon,
  UserRound,
  X,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

import {
  formatChangeRate,
  formatKrwPrice,
} from "../lib/formatters";
import type { MarketRow } from "../types";

type PersonalInfoPanelProps = {
  markets: MarketRow[];
};

const alertEvents = [
  { label: "KRW-DOGE 24H 상승률 3% 돌파", time: "16:42", tone: "rise" },
  { label: "KRW-BTC 24H 고가 갱신", time: "16:38", tone: "rise" },
  { label: "KRW-ETH 24H 저가 근접", time: "16:31", tone: "fall" },
] as const;

export function PersonalInfoPanel({ markets }: PersonalInfoPanelProps) {
  const favorites = markets.filter((market) => market.favorite).slice(0, 3);
  const recentMarkets = markets.filter((market) => !market.favorite).slice(2, 5);

  return (
    <Card className="flex h-full min-h-[680px] flex-col overflow-hidden rounded-md border-border bg-card shadow-none">
      <CardHeader className="flex-row items-center justify-between border-b border-border px-4 py-4">
        <CardTitle className="text-[17px] font-extrabold">내 정보</CardTitle>
        <Button variant="ghost" size="icon" aria-label="내 정보 닫기">
          <X data-icon="icon" />
        </Button>
      </CardHeader>

      <CardContent className="min-h-0 flex-1 p-0">
        <ScrollArea className="h-full">
          <div className="flex flex-col gap-3 p-3">
            <Tabs value="personal" className="w-full">
              <TabsList className="grid h-9 w-full grid-cols-3 rounded-md bg-muted p-1">
                <TabsTrigger value="personal" className="h-7 text-[12px]">
                  개인 투자
                </TabsTrigger>
                <TabsTrigger value="interest" className="h-7 text-[12px]">
                  관심
                </TabsTrigger>
                <TabsTrigger value="recent" className="h-7 text-[12px]">
                  최근
                </TabsTrigger>
              </TabsList>
            </Tabs>

            <section className="rounded-md border border-border bg-background p-3">
              <h3 className="mb-3 text-[14px] font-bold">개인 투자 요약</h3>
              <div className="flex gap-3 rounded-md bg-muted p-4">
                <div className="flex size-10 items-center justify-center rounded-full bg-accent text-primary">
                  <UserRound data-icon="icon" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-[14px] font-extrabold text-primary">공개 시세 모드</div>
                  <p className="mt-1 text-[12px] font-medium leading-5 text-muted-foreground">
                    투자 정보 연결 전입니다. 거래 및 보유 현황 기능은 연결 후 이용할 수 있어요.
                  </p>
                  <Button variant="outline" size="sm" className="mt-3">
                    연결 안내 보기
                  </Button>
                </div>
              </div>
            </section>

            <section className="rounded-md border border-border bg-background p-3">
              <div className="mb-2 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <h3 className="text-[14px] font-bold">관심 내역</h3>
                  <Badge variant="secondary" className="rounded-md px-2 py-0.5">
                    {favorites.length}
                  </Badge>
                </div>
                <Button variant="link" size="sm" className="h-7 px-0 text-[12px]">
                  편집
                </Button>
              </div>
              <div className="flex flex-col">
                {favorites.map((market) => (
                  <MarketSummaryRow key={market.market} market={market} />
                ))}
              </div>
            </section>

            <section className="rounded-md border border-border bg-background p-3">
              <div className="mb-2 flex items-center gap-2">
                <h3 className="text-[14px] font-bold">최근 본 종목</h3>
                <Badge variant="secondary" className="rounded-md px-2 py-0.5">
                  {recentMarkets.length}
                </Badge>
              </div>
              <div className="flex flex-col">
                {recentMarkets.map((market) => (
                  <MarketSummaryRow key={market.market} market={market} compact />
                ))}
              </div>
            </section>

            <section className="rounded-md border border-border bg-background p-3">
              <div className="mb-2 flex items-center justify-between">
                <h3 className="text-[14px] font-bold">알림 이벤트</h3>
                <Button variant="link" size="sm" className="h-7 px-0 text-[12px]">
                  전체 보기
                </Button>
              </div>
              <div className="flex flex-col gap-3">
                {alertEvents.map((event) => (
                  <div key={event.label} className="flex items-center gap-3 text-[13px]">
                    <span
                      className="flex size-6 items-center justify-center rounded-full data-[tone=fall]:bg-fall/10 data-[tone=fall]:text-fall data-[tone=rise]:bg-rise/10 data-[tone=rise]:text-rise"
                      data-tone={event.tone}
                    >
                      {event.tone === "rise" ? <ArrowUp data-icon="icon" /> : <ArrowDown data-icon="icon" />}
                    </span>
                    <span className="min-w-0 flex-1 truncate font-bold">{event.label}</span>
                    <span className="tabular-nums text-muted-foreground">{event.time}</span>
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-md border border-border bg-background p-3">
              <h3 className="mb-3 text-[14px] font-bold">로컬 설정</h3>
              <div className="flex flex-col gap-3">
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2 text-[13px] font-semibold">
                    <Moon data-icon="icon" />
                    다크 모드
                  </div>
                  <Switch aria-label="다크 모드" />
                </div>
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2 text-[13px] font-semibold">
                    <CalendarClock data-icon="icon" />
                    새로고침 주기
                  </div>
                  <Button variant="outline" size="sm" className="min-w-[92px] justify-between gap-2">
                    5초
                    <ChevronDown data-icon="inline-end" />
                  </Button>
                </div>
              </div>
            </section>
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}

function MarketSummaryRow({
  market,
  compact = false,
}: {
  market: MarketRow;
  compact?: boolean;
}) {
  const side = market.changeRate > 0 ? "rise" : market.changeRate < 0 ? "fall" : "flat";

  return (
    <div className="grid min-h-9 grid-cols-[20px_minmax(74px,1fr)_80px_58px] items-center gap-2 text-[12px]">
      <span className="flex items-center justify-center text-muted-foreground">
        {compact ? <Flame data-icon="icon" /> : <span className="text-amber-400">★</span>}
      </span>
      <div className="min-w-0">
        <div className="truncate font-extrabold">{market.market}</div>
        <div className="truncate text-[11px] font-medium text-muted-foreground">{market.koreanName}</div>
      </div>
      <span className="text-right font-bold tabular-nums">{formatKrwPrice(market.currentPrice)}</span>
      <span
        className="text-right font-bold tabular-nums data-[side=fall]:text-fall data-[side=rise]:text-rise"
        data-side={side}
      >
        {formatChangeRate(market.changeRate)}
      </span>
    </div>
  );
}
