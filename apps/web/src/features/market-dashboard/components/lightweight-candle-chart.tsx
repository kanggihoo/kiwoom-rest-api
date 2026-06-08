"use client";

import { useEffect, useRef } from "react";
import {
  CandlestickSeries,
  createChart,
  HistogramSeries,
  type IChartApi,
  type Time,
} from "lightweight-charts";

import { formatKrwPrice, formatMarketSize } from "../lib/formatters";
import type { CandlePoint } from "../types";

type LightweightCandleChartProps = {
  candles: CandlePoint[];
};

function readCssVariable(name: string, fallback: string) {
  if (typeof window === "undefined") {
    return fallback;
  }

  const value = window.getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return value || fallback;
}

export function LightweightCandleChart({ candles }: LightweightCandleChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const hoverCandle = candles[Math.floor(candles.length * 0.78)] ?? candles[0];
  const lastCandle = candles[candles.length - 1];
  const hoverDate = hoverCandle
    ? new Date(hoverCandle.time * 1000).toISOString().slice(0, 10)
    : "2025-06-02";

  useEffect(() => {
    const container = containerRef.current;

    if (!container) {
      return;
    }

    const foreground = readCssVariable("--foreground", "#151b2d");
    const muted = readCssVariable("--muted-foreground", "#7b8494");
    const border = readCssVariable("--border", "#e3e8f0");
    const background = readCssVariable("--card", "#ffffff");
    const rise = readCssVariable("--chart-3", "#f04452");
    const fall = readCssVariable("--chart-2", "#1d6fff");

    const chart = createChart(container, {
      autoSize: true,
      height: 430,
      layout: {
        background: { color: background },
        textColor: muted,
        fontFamily: "var(--font-pretendard), Pretendard, system-ui, sans-serif",
        fontSize: 12,
      },
      grid: {
        vertLines: { color: border },
        horzLines: { color: border },
      },
      rightPriceScale: {
        borderColor: border,
      },
      timeScale: {
        borderColor: border,
        timeVisible: true,
        secondsVisible: false,
      },
      crosshair: {
        horzLine: { color: foreground, labelBackgroundColor: foreground },
        vertLine: { color: foreground, labelBackgroundColor: foreground },
      },
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: rise,
      downColor: fall,
      borderUpColor: rise,
      borderDownColor: fall,
      wickUpColor: rise,
      wickDownColor: fall,
      priceFormat: {
        type: "price",
        precision: 0,
        minMove: 1,
      },
    });

    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: {
        type: "volume",
      },
      priceScaleId: "",
    });

    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.82,
        bottom: 0,
      },
    });

    candleSeries.setData(
      candles.map((candle) => ({
        time: candle.time as Time,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
      })),
    );

    volumeSeries.setData(
      candles.map((candle) => ({
        time: candle.time as Time,
        value: candle.volume,
        color: candle.close >= candle.open ? `${rise}55` : `${fall}55`,
      })),
    );

    chart.timeScale().fitContent();

    chartRef.current = chart;

    return () => {
      chart.remove();
      chartRef.current = null;
    };
  }, [candles]);

  return (
    <div className="relative min-h-[430px]">
      <div ref={containerRef} className="h-[430px] w-full" aria-label="Mock candle chart" />
      {hoverCandle ? (
        <div className="pointer-events-none absolute left-[52%] top-[34%] rounded-md border border-border bg-card/95 px-4 py-3 text-[12px] shadow-sm">
          <div className="mb-2 font-bold text-foreground">{hoverDate}</div>
          <dl className="grid grid-cols-[44px_86px] gap-x-3 gap-y-1">
            <dt className="text-muted-foreground">시가</dt>
            <dd className="text-right font-semibold tabular-nums">{formatKrwPrice(hoverCandle.open)}</dd>
            <dt className="text-muted-foreground">고가</dt>
            <dd className="text-right font-semibold tabular-nums text-rise">{formatKrwPrice(hoverCandle.high)}</dd>
            <dt className="text-muted-foreground">저가</dt>
            <dd className="text-right font-semibold tabular-nums text-fall">{formatKrwPrice(hoverCandle.low)}</dd>
            <dt className="text-muted-foreground">종가</dt>
            <dd className="text-right font-semibold tabular-nums text-primary">{formatKrwPrice(hoverCandle.close)}</dd>
            <dt className="text-muted-foreground">거래량</dt>
            <dd className="text-right font-semibold tabular-nums">{formatMarketSize(hoverCandle.volume)}</dd>
          </dl>
        </div>
      ) : null}
      {lastCandle ? (
        <div className="pointer-events-none absolute inset-y-4 right-[25%] border-l border-dashed border-primary/45">
          <span className="absolute left-2 top-[42%] rounded-[4px] bg-primary px-2 py-1 text-[12px] font-bold tabular-nums text-primary-foreground">
            {formatKrwPrice(lastCandle.close)}
          </span>
        </div>
      ) : null}
    </div>
  );
}
