import { cn } from "@/lib/utils";

type SparklineProps = {
  values: number[];
  className?: string;
  variant?: "rise" | "fall" | "muted";
};

function toPath(values: number[]) {
  const width = 72;
  const height = 28;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  return values
    .map((value, index) => {
      const x = (index / (values.length - 1)) * width;
      const y = height - ((value - min) / range) * height;
      return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
}

export function Sparkline({ values, className, variant = "muted" }: SparklineProps) {
  const strokeClass =
    variant === "rise"
      ? "stroke-rise"
      : variant === "fall"
        ? "stroke-fall"
        : "stroke-muted-foreground";

  return (
    <svg
      viewBox="0 0 72 28"
      role="img"
      aria-label="추세선"
      className={cn("h-7 w-[72px] overflow-visible", className)}
    >
      <path
        d={toPath(values)}
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={cn("stroke-[1.8]", strokeClass)}
      />
    </svg>
  );
}
