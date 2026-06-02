import type { IndexStripItem } from "../types";
import { formatChangeRate } from "../lib/formatters";
import { Sparkline } from "./sparkline";

type IndexStripProps = {
  indexes: IndexStripItem[];
};

export function IndexStrip({ indexes }: IndexStripProps) {
  return (
    <section className="border-b border-border bg-background px-5 py-2" aria-label="Market indexes">
      <div className="grid grid-cols-6 overflow-hidden rounded-md border border-border bg-card">
        {indexes.map((item) => (
          <article
            key={item.label}
            className="grid min-h-[76px] grid-cols-[1fr_auto] items-center gap-3 border-r border-border px-5 last:border-r-0"
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
      </div>
    </section>
  );
}
