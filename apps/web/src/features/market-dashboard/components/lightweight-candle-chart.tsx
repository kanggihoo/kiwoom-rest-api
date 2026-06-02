"use client";

import { useEffect, useRef } from "react";
import {
  CandlestickSeries,
  createChart,
  HistogramSeries,
  type IChartApi,
  type Time,
} from "lightweight-charts";

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
    <div className="relative min-h-[430px] border-t border-border">
      <div ref={containerRef} className="h-[430px] w-full" aria-label="Mock candle chart" />
    </div>
  );
}
