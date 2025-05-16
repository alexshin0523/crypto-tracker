import os
import time
from datetime import timedelta
import faust
import re

from aggregator.models import Candle, Trade
from confluent_kafka.admin import AdminClient, NewTopic

# Set up Defaults
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
PARTITIONS = int(os.getenv("PARTITIONS", "1"))
TOTAL_REPLICAS = int(os.getenv("TOTAL_REPLICAS", "1"))
INTERVALS = {
    "1s": timedelta(seconds=1),
    "1m": timedelta(minutes=1),
    "1h": timedelta(hours=1),
}

# Create Candle topics
print("start candle topic creation _______________________________________________")
admin = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP})

SYMBOLS = []
topic_list = []
while not SYMBOLS:
    topic_list = admin.list_topics(timeout=10).topics
    SYMBOLS = {name.split('.', 1)[1] for name in topic_list if name.startswith("trades.")}

new_topics = []
for interval in INTERVALS:
    for symbol in SYMBOLS:
        topic = f"candles.{interval}.{symbol}"
        print(f"checking topic: {topic}")
        if topic not in topic_list:
            print(f"{topic} needs to be added")
            new_topic = NewTopic(topic, num_partitions=PARTITIONS, replication_factor=TOTAL_REPLICAS)
            new_topics.append(new_topic)
if new_topics:
    topic_creation_futures = admin.create_topics(new_topics)
    for topic_name, creation_future in topic_creation_futures.items():
        try:
            creation_future.result()
            print(f"Created topic {topic_name}")
        except Exception as e:
            print(f"Failed to create topic {topic_name}: {e}")

# Set up Faust
app = faust.App(
    'crypto_aggregator',
    broker=f"kafka://{KAFKA_BOOTSTRAP}",
    store="rocksdb://",
    topic_partitions=PARTITIONS,
)

# Define topics and tables dynamically
trade_topics_list = [f"trades.{s}" for s in SYMBOLS]
trades_topic = app.topic(*trade_topics_list, value_type=Trade)

#Create one tumbling table & output topic per interval
tables = {}
out_topics = {}
for interval_name, delta in INTERVALS.items():
    tables[interval_name] = (
        app.Table(
            f"candle_{interval_name}",
            default=lambda: {
                'open': None,
                'high': float('-inf'),
                'low': float('inf'),
                'close': None,
                'volume': 0.0,
                'count': 0,
                'first_ts': None,
            },
            partitions=PARTITIONS,
        ).tumbling(delta, expires=delta * 60)
    )
    for symbol in SYMBOLS:
        out_topics[(interval_name, symbol)] = app.topic(
            f"candles.{interval_name}.{symbol}",
            key_type=str,
            value_type=Candle,
            partitions=PARTITIONS,
        )

@app.agent(trades_topic)
async def process(trades):
    async for trade in trades.group_by(Trade.s):
        symbol = trade.s
        event_time = trade.E

        for interval_name, table in tables.items():
            size = INTERVALS[interval_name]
            candle_group = table[symbol]
            # Get the current candle for the symbol
            candle = candle_group.current()
            if candle['open'] is None:
                candle['open'] = trade.p
                candle['first_ts'] = event_time
            candle['high'] = max(candle['high'], trade.p)
            candle['low'] = min(candle['low'], trade.p)
            candle['close'] = trade.p
            candle['volume'] = trade.q
            candle['count'] += 1

            # Check if the window has ended
            if candle_group.delta() >= candle_group.size.total_second():
                # Create new candle
                candle = Candle(
                    symbol=symbol,
                    interval=interval_name,
                    window_start=int(candle_group.expires.timestamp() * 1000) - int(size.totalseconds() * 1000),
                    open=candle['open'],
                    high=candle['high'],
                    low=candle['low'],
                    close=candle['close'],
                    volume=candle['volume'],
                    trade_count=candle['count'],
                    processing_latency_ms = (time.time() * 1000) - candle['first_ts'],
                )
                #Emit and reset candle
                await out_topics[(interval_name, symbol)].send(key=symbol, value=candle)
                candle_group.current().reset()

if __name__ == "__main__":
    app.main()


