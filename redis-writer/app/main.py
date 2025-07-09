import json, signal, time
from confluent_kafka import Consumer
from confluent_kafka.admin import AdminClient
from config import KAFKA_BOOTSTRAP, GROUP_ID, REDIS_HOST, REDIS_PORT
from redis_writer import get_ts_client, write_candle_to_redis

ts = get_ts_client(REDIS_HOST, REDIS_PORT)
consumer = Consumer({
    'bootstrap.servers': KAFKA_BOOTSTRAP,
    'group.id': GROUP_ID,
    'auto.offset.reset': 'earliest'
})
admin = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP})
topics = None
while not topics:
    print("grabbing topics list...")
    topics  = admin.list_topics(timeout=5).topics
    if not topics:
        time.sleep(.2)
candle_topics = [name for name in topics if name.startswith("candles.")]
consumer.subscribe(candle_topics)

running = True
def shutdown(sig, frame):
    global running
    running = False
signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

def main():
    print("Consuming messages...")
    while running:
        msg = consumer.poll(1.0)
        if msg and not msg.error():
            try:
                candle = json.loads(msg.value().decode('utf-8'))
                write_candle_to_redis(ts, candle)
                print(f"Wrote candle {candle['symbol']} {candle['interval']} {candle['window_start']}")
            except Exception as e:
                print(f"Error: {e}")
    consumer.close()

if __name__ == "__main__":
    main()
