import React, { useState, useEffect, useRef } from "react";
import ControlBar from "../components/ControlBar";
import Chart, { Candle } from "../components/Chart";

const SYMBOLS = ["BTCUSDT"];
const INTERVALS = ["1s", "1m", "1h"];

type CandlesMap = Record<string, Candle[]>;

export default function Home() {
  const [symbol, setSymbol] = useState(SYMBOLS[0]);
  const [interval, setInterval] = useState(INTERVALS[1]);
  const [candlesMap, setCandlesMap] = useState<CandlesMap>({});
  const [hoveredCandle, setHoveredCandle] = useState<Candle | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Fetch on mount and when symbol changes
  useEffect(() => {
    const fetchCandles = async () => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      const url = `${apiUrl}/ohlcv/?symbols=${symbol}&count=150`;
      const res = await fetch(url);
      const data = await res.json();
      setCandlesMap(data[symbol] || {});
    };
    fetchCandles();
  }, [symbol]);

  // Real-time WebSocket updates
  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws';
    const wsUrl =
      apiUrl.replace(/^http/, wsProtocol).replace(/\/$/, "") + "/ws/candles";
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const candle = JSON.parse(event.data);
      if (candle.symbol === symbol && INTERVALS.includes(candle.interval)) {
        console.log('New candle received:', candle);
        setCandlesMap((prev) => {
          const arr = prev[candle.interval] ? [...prev[candle.interval]] : [];
          const idx = arr.findIndex(
            (c) => c.window_start === candle.window_start
          );
          if (idx !== -1) arr[idx] = candle;
          else arr.push(candle);
          // Sort and keep only latest 150
          const sortedArr = arr
            .sort((a, b) => a.window_start - b.window_start)
            .slice(-150);
          return { ...prev, [candle.interval]: sortedArr };
        });
      }
    };

    ws.onerror = (e) => {
      console.error("WebSocket error:", e);
    };
    return () => ws.close();
  }, [symbol]);

  const candles = candlesMap[interval] || [];

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center py-8">
      <div className="w-full max-w-3xl shadow-xl rounded-xl bg-gray-800">
        <ControlBar
          symbols={SYMBOLS}
          symbol={symbol}
          onSymbolChange={setSymbol}
          interval={interval}
          onIntervalChange={setInterval}
        />
        <div className="relative">
          <Chart data={candles} onCrosshairMove={setHoveredCandle} />
          {/* Overlay for crosshair popups */}
          {hoveredCandle && (
            <div className="absolute right-2 top-2 p-2 bg-gray-900/80 rounded text-sm border border-gray-700 z-10">
              <div>
                <b>Time:</b>{" "}
                {new Date(hoveredCandle.window_start).toLocaleString()}
              </div>
              <div>
                <b>Open:</b> {hoveredCandle.open}
              </div>
              <div>
                <b>High:</b> {hoveredCandle.high}
              </div>
              <div>
                <b>Low:</b> {hoveredCandle.low}
              </div>
              <div>
                <b>Close:</b> {hoveredCandle.close}
              </div>
              <div>
                <b>Volume:</b> {hoveredCandle.volume}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
