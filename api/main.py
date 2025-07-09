from fastapi import FastAPI, Query
from typing import List, Dict, Any
from redis import Redis
from redistimeseries.client import Client as RedisTimeSeries
import os

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

r = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
ts = RedisTimeSeries(conn=r)

OHLCV_FIELDS = ["open", "high", "low", "close", "volume"]
INTERVALS = ["1s", "1m", "1h"]

@app.get("/ohlcv/")
def get_multi_candles(
        symbols: List[str] = Query(..., description="List of symbols"),
        count: int = 150
) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    result = {}
    for symbol in symbols:
        result[symbol] = {}
        for interval in INTERVALS:
            candles_map = {}
            # For each field, get the latest N
            field_candles = {}
            for field in OHLCV_FIELDS:
                key = f"ohlcv:{symbol}:{interval}:{field}"
                try:
                    entries = ts.revrange(key, "-", "+", count=count)
                except Exception:
                    entries = []
                # reversed to get oldest first
                field_candles[field] = list(reversed(entries))
            # Merge by timestamp to get full OHLCV per candle
            merged_candles = []
            # Find all timestamps (union of all fields)
            timestamps = set()
            for v in field_candles.values():
                timestamps.update(ts_ for ts_, _ in v)
            for ts_ in sorted(timestamps):
                candle = {"window_start": int(ts_)}
                for field in OHLCV_FIELDS:
                    # Find value for this ts_ in each field
                    val = next((float(v) for t, v in field_candles[field] if t == ts_), None)
                    candle[field] = val
                merged_candles.append(candle)
            result[symbol][interval] = merged_candles
    return result
