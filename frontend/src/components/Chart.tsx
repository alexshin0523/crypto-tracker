import React, { useEffect, useRef } from "react";
import {
  createChart,
  IChartApi,
  Time,
  CandlestickSeriesOptions,
  CrosshairMode,
  MouseEventParams,
} from "lightweight-charts";

export type Candle = {
  window_start: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

type Props = {
  data: Candle[];
  onCrosshairMove?: (candle: Candle | null) => void;
};

export default function Chart({ data, onCrosshairMove }: Props) {
  const chartContainer = useRef<HTMLDivElement>(null);
  const chartApi = useRef<IChartApi | null>(null);
  const seriesRef = useRef<any>(null);

  useEffect(() => {
    console.log("Chart re-rendered with", data.length, "candles", data);
    if (!chartContainer.current) return;
    // Create chart
    const chart = createChart(chartContainer.current, {
      height: 400,
      width: chartContainer.current.clientWidth,
      layout: { background: { color: "#222" }, textColor: "#DDD" },
      grid: { vertLines: { color: "#333" }, horzLines: { color: "#333" } },
      crosshair: { mode: CrosshairMode.Normal },
    });

    chartApi.current = chart;

    // Add candlestick series
    seriesRef.current = chart.addCandlestickSeries({
      upColor: "#26a69a",
      downColor: "#ef5350",
      borderVisible: false,
      wickUpColor: "#26a69a",
      wickDownColor: "#ef5350",
    } as CandlestickSeriesOptions);

    // Set data
    const seriesData = data.map((d) => ({
      time: Math.floor(d.window_start / 1000) as Time,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));
    seriesRef.current.setData(seriesData);

    // Crosshair handler
    const crosshairHandler = (param: MouseEventParams) => {
      if (!param.time) {
        onCrosshairMove?.(null);
        return;
      }
      const ts = (param.time as number) * 1000;
      const candle = data.find((d) => d.window_start === ts);
      onCrosshairMove?.(candle || null);
    };
    chart.subscribeCrosshairMove(crosshairHandler);

    // Resize handler
    const handleResize = () => {
      chart.resize(chartContainer.current!.clientWidth, 400);
    };
    window.addEventListener("resize", handleResize);

    // Cleanup
    return () => {
      chart.unsubscribeCrosshairMove(crosshairHandler);
      window.removeEventListener("resize", handleResize);
      chart.remove();
      chartApi.current = null;
    };
    // eslint-disable-next-line
  }, [data, onCrosshairMove]);

  return (
    <div
      ref={chartContainer}
      className="rounded-b-xl"
      style={{ width: "100%", background: "#222" }}
    />
  );
}
