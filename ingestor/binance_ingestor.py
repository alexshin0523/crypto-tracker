from confluent_kafka import Producer, KafkaException
from confluent_kafka.admin import AdminClient, NewTopic
import asyncio, json, os, signal, sys
from aiohttp import web
import websockets

FULL_LIST = os.getenv("FULL_SYMBOLS", "").split(",")
TOTAL = int(os.getenv("TOTAL_REPLICAS", "1"))
ORD  = int(os.getenv("POD_ORDINAL",   "0"))

# grab the symbols whose index % TOTAL matches this pod’s ORD
SYMBOLS = [
    sym for idx, sym in enumerate(FULL_LIST)
    if (idx % TOTAL) == ORD
]
BINANCE_WS = "wss://fstream.binance.com/stream"

# ----- Kafka setup -----
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

producer_conf = {"bootstrap.servers": KAFKA_BOOTSTRAP}
producer = Producer(producer_conf)

admin = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP})
existing = admin.list_topics(timeout=5).topics.keys()
new_topics = [
    NewTopic(f"trades.{s}", num_partitions=1, replication_factor=1)
    for s in SYMBOLS if f"trades.{s}" not in existing
]
if new_topics:
    fs = admin.create_topics(new_topics)
    for topic, f in fs.items():
        try:
            f.result()
            print(f"Created topic {topic}")
        except KafkaException as e:
            print(f"Topic {topic} creation failed: {e}")

# ----- health-check server -----
async def health_server():
    async def handler(request):
        return web.Response(text="ok")
    app = web.Application()
    app.add_routes([web.get('/alive', handler)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

# ----- websocket consumer -----
async def ingest(symbols):
    # Binance lets us multiplex many streams with one connection:
    stream_names = "/".join(f"{s.lower()}@trade" for s in symbols)
    url = f"{BINANCE_WS}?streams={stream_names}"
    while True:
        try:
            async with websockets.connect(url, ping_interval=15) as ws:
                async for msg in ws:
                    event = json.loads(msg)["data"]
                    topic = f"trades.{event['s']}"
                    producer.produce(
                        topic=topic,
                        key=event["s"].encode(),
                        value=json.dumps(event),
                        on_delivery=lambda err, msg: (
                            print(f"DELIVERY failed: {err}") if err else None
                        )
                    )
                    # flush immediately to avoid buffering
                    producer.poll(0)
        except Exception as e:
            print("WS error – reconnecting:", e, file=sys.stderr)
            await asyncio.sleep(3)




async def main():
    await asyncio.gather(
        health_server(),
        ingest(SYMBOLS)
    )

if __name__ == "__main__":
    def shutdown(signum, frame):
        asyncio.get_event_loop().stop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, shutdown)
    asyncio.run(main())