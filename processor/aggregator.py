from confluent_kafka.admin import AdminClient
from pyflink.common import Duration, Types, WatermarkStrategy
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.window import TumblingEventTimeWindows
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.time import Time
from .config import KAFKA_BOOTSTRAP, MAX_OUT_OF_ORDER_MS
from .deserializer import json_to_trade
from .timestampers import TradeTimestampAssigner
from .window_functions import OHLCVWindowFunction
from .schema import CANDLE_TYPE, candle_to_row
import json, time

def build(env: StreamExecutionEnvironment):
    admin = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP})
    topics_list = []
    while not topics_list:
        print("grabbing topics list...")
        topics_list  = admin.list_topics(timeout=5)
        time.sleep(1)

    trade_topics = [name for name in topics_list.topics
                    if name.startswith("trades.")]
    print(trade_topics)
    consumer_props = {
        "bootstrap.servers": KAFKA_BOOTSTRAP,
        "group.id": "processor",
        "auto.offset.reset": "earliest",
    }

    print("Creating Flink Kafka consumer...")
    consumer = FlinkKafkaConsumer(
        topics=trade_topics,
        deserialization_schema=SimpleStringSchema(),  # raw JSON
        properties=consumer_props,
    )

    print("Creating Flink DataStream...")
    ds = (
        env
        .add_source(consumer)
        .map(json_to_trade, output_type=Types.PICKLED_BYTE_ARRAY())
        .assign_timestamps_and_watermarks(
            WatermarkStrategy
            .for_bounded_out_of_orderness(Duration.of_millis(MAX_OUT_OF_ORDER_MS))
            .with_timestamp_assigner(TradeTimestampAssigner())
        )
        .key_by(lambda t: t.symbol)
        .window(TumblingEventTimeWindows.of(Time(60_000)))
        .process(OHLCVWindowFunction(),
                 output_type=CANDLE_TYPE)
    )

    print("Creating Flink Kafka producer...")
    producer = FlinkKafkaProducer(
        topic="candles.1m",
        serialization_schema=SimpleStringSchema(),
        producer_config={"bootstrap.servers": KAFKA_BOOTSTRAP},
    )

    print("Adding sink...")
    ds.map(lambda c: json.dumps(c.__dict__)).add_sink(producer)
