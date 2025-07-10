from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
from redis import Redis
from redistimeseries.client import Client as RedisTimeSeries
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import asyncio

from confluent_kafka import Consumer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
CANDLE_TOPICS = ["candles.1s", "candles.1m", "candles.1h"]  # adjust to your topic names

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

@app.websocket("/ws/candles")
async def candles_ws(websocket: WebSocket):
    await websocket.accept()
    print("connection open")
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP,
        'group.id': "api-ws-candle-group",
        'auto.offset.reset': 'latest'
    })
    consumer.subscribe(CANDLE_TOPICS)
    try:
        while True:
            try:
                msg = consumer.poll(0.5)
                if msg and not msg.error():
                    try:
                        candle = json.loads(msg.value().decode("utf-8"))
                        await websocket.send_json(candle)
                    except RuntimeError as e:
                        print("WebSocket is closed, exiting loop:", e)
                        break  # Stop loop immediately if socket closed
                    except Exception as e:
                        print("Bad message or decode error:", e)
                await asyncio.sleep(0.1)
            except WebSocketDisconnect:
                print("WebSocket disconnected")
                break
    finally:
        consumer.close()
        print("connection closed")