import {
  ToggleGroup,
  ToggleGroupItem,
} from "@/components/ui/toggle-group";

import type { CandleUnit } from "../types";

const candleUnits: Array<{ value: CandleUnit; label: string }> = [
  { value: "1m", label: "1분" },
  { value: "5m", label: "5분" },
  { value: "15m", label: "15분" },
  { value: "1h", label: "1시간" },
  { value: "1d", label: "1일" },
  { value: "1w", label: "1주" },
];

type CandleUnitToggleProps = {
  value: CandleUnit;
};

export function CandleUnitToggle({ value }: CandleUnitToggleProps) {
  return (
    <ToggleGroup type="single" value={value} aria-label="Candle unit" className="gap-1">
      {candleUnits.map((unit) => (
        <ToggleGroupItem key={unit.value} value={unit.value} className="h-8 px-3 text-[13px]">
          {unit.label}
        </ToggleGroupItem>
      ))}
    </ToggleGroup>
  );
}
