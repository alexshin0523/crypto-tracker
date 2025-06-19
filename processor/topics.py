import time
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.cimpl import NewPartitions

from .config import KAFKA_BOOTSTRAP, DESIRED_PARTITIONS, WINDOW_CONFIGS

def discover_topics(admin: AdminClient) -> dict:
    topics = None
    while not topics:
        print("grabbing topics list...")
        topics  = admin.list_topics(timeout=5).topics
        if not topics:
            time.sleep(.2)
    return topics

def get_topic_names(md: dict, prefix: str = "trades.") -> list:
    return [t for t in md.topics if t.startswith(prefix)]


def create_interval_topics(admin: AdminClient, topics: dict):
    for interval, _ in WINDOW_CONFIGS:
        topic = f"candles.{interval}"
        if topic not in topics:
            new_topic = NewTopic(topic, num_partitions=DESIRED_PARTITIONS, replication_factor=1)
            admin.create_topics([new_topic]).get(topic).result()
        else:
            current = len(topics[topic].partitions)
            if current < DESIRED_PARTITIONS:
                admin.create_partitions([NewPartitions(topic, DESIRED_PARTITIONS)]).get(topic).result()