from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.state_backend import EmbeddedRocksDBStateBackend
from pyflink.common import Configuration
from . import aggregator, config
from .config import STATE_DIR
import os

def main():
    cfg = Configuration()
    cfg.set_string("state.backend", "rocksdb")                       # or hashmap
    cfg.set_string("state.checkpoint-storage", "filesystem")
    cfg.set_string("state.checkpoints.dir", STATE_DIR)

    env = StreamExecutionEnvironment.get_execution_environment()
    env.add_jars(f"file://{os.getenv('CONNECTOR_JAR')}")
    env.enable_checkpointing(30_000)  # ms
    env.configure(cfg)

    aggregator.build(env)
    env.execute("crypto-ticker-processor")

if __name__ == "__main__":
    main()