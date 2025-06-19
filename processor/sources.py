from typing import List
import time
from confluent_kafka.admin import AdminClient
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
from .config import KAFKA_BOOTSTRAP


def create_trade_consumer(
        topics: List[str],
        group_id: str = "processor",
        auto_offset_reset: str = "earliest",
) -> FlinkKafkaConsumer:
    print("Creating Flink Kafka consumer for topics " + str(topics))
    props = {
        "bootstrap.servers": KAFKA_BOOTSTRAP,
        "group.id": group_id,
        "auto.offset.reset": auto_offset_reset,
    }
    return FlinkKafkaConsumer(
        topics=topics,
        deserialization_schema=SimpleStringSchema(),
        properties=props,
    )