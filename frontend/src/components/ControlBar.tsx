import React from "react";

type Props = {
  symbols: string[];
  symbol: string;
  onSymbolChange: (s: string) => void;
  interval: string;
  onIntervalChange: (i: string) => void;
};

const INTERVALS = ["1s", "1m", "1h"];

export default function ControlBar({
  symbols,
  symbol,
  onSymbolChange,
  interval,
  onIntervalChange,
}: Props) {
  return (
    <div className="flex items-center gap-4 p-4 bg-gray-800 text-white rounded-t-xl">
      <label>
        Symbol:
        <select
          value={symbol}
          onChange={(e) => onSymbolChange(e.target.value)}
          className="ml-2 px-2 py-1 rounded bg-gray-700"
        >
          {symbols.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </label>
      <div className="ml-4 flex gap-2">
        {INTERVALS.map((intv) => (
          <button
            key={intv}
            className={`px-3 py-1 rounded ${
              interval === intv
                ? "bg-blue-500 text-white font-bold"
                : "bg-gray-700 text-gray-200"
            }`}
            onClick={() => onIntervalChange(intv)}
          >
            {intv}
          </button>
        ))}
      </div>
    </div>
  );
}
