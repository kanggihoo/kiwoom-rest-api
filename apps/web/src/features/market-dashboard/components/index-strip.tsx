import { Settings } from "lucide-react";

import { Button } from "@/components/ui/button";

import type { IndexStripItem } from "../types";
import { formatChangeRate } from "../lib/formatters";
import { Sparkline } from "./sparkline";

type IndexStripProps = {
  indexes: IndexStripItem[];
};

export function IndexStrip({ indexes }: IndexStripProps) {
  const visibleIndexes = indexes.slice(0, 5);

  return (
    <section className="border-b border-border bg-background px-5 py-3" aria-label="Market indexes">
      <div className="grid grid-cols-[repeat(5,minmax(150px,1fr))_64px] overflow-hidden rounded-md border border-border bg-card">
        {visibleIndexes.map((item) => (
          <article
            key={item.label}
            className="grid min-h-[76px] grid-cols-[1fr_auto] items-center gap-3 border-r border-border px-5"
          >
            <div className="flex flex-col gap-1">
              <span className="text-[12px] font-semibold text-muted-foreground">{item.label}</span>
              <div className="flex items-baseline gap-3">
                <strong className="font-sans text-[18px] font-bold leading-none tabular-nums">
                  {item.value}
                </strong>
                <span
                  className="text-[13px] font-semibold tabular-nums data-[side=fall]:text-fall data-[side=rise]:text-rise"
                  data-side={item.side}
                >
                  {formatChangeRate(item.changeRate)}
                </span>
              </div>
            </div>
            <Sparkline
              values={item.sparkline}
              variant={item.side === "rise" ? "rise" : item.side === "fall" ? "fall" : "muted"}
            />
          </article>
        ))}
        <div className="flex items-center justify-center">
          <Button variant="ghost" size="icon" aria-label="Index strip settings">
            <Settings data-icon="icon" />
          </Button>
        </div>
      </div>
    </section>
  );
}
