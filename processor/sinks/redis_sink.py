import json
from redis import Redis, ConnectionPool
from pyflink.datastream.functions import SinkFunction, RuntimeContext

from ..config import REDIS_URL


class RedisCandleSink(SinkFunction):
    """
    A sink function that writes finalized candles into Redis:
      - Closed candles into a ZSET for history
      - Latest in-flight candle into a HASH for quick UI reads
    """
    def __init__(self, redis_url: str = REDIS_URL, history_size: int = 500):
        self.redis_url = redis_url
        self.history_size = history_size
        self.client = None

    def open(self, runtime_context: RuntimeContext):
        # 1) Create a ConnectionPool for efficient reuse per subtask
        pool = ConnectionPool.from_url(self.redis_url)
        # 2) Use the pool for thread-safe, multiplexed connections
        self.client = Redis(connection_pool=pool)

    def invoke(self, candle_json: str, context):
        # Parse the JSON string back into a dict
        data = json.loads(candle_json)
        interval = data["interval"]
        symbol   = data["symbol"]
        start    = data["window_start"]

        # -- Hot history: Sorted Set of closed candles --
        zkey = f"candles:{interval}:{symbol}"
        # Member: full JSON, Score: window_start timestamp
        self.client.zadd(zkey, {candle_json: start})
        # Trim to keep only the most recent N entries
        self.client.zremrangebyrank(zkey, 0, -self.history_size - 1)

        # -- In-flight: Hash for the current candle --
        hkey = f"candles:current:{interval}:{symbol}"
        self.client.hset(hkey, mapping={
            "open":         data["open"],
            "high":         data["high"],
            "low":          data["low"],
            "close":        data["close"],
            "volume":       data["volume"],
            "window_start": data["window_start"],
            "window_end":   data["window_end"],
        })

    def close(self):
        if self.client:
            # Properly close connections if needed
            self.client.close()