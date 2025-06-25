from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.state_backend import EmbeddedRocksDBStateBackend
from pyflink.common import Configuration
from processor import aggregator, config
from processor.config import STATE_DIR, DESIRED_PARTITIONS
import os

def create_env() -> StreamExecutionEnvironment:
    env = StreamExecutionEnvironment.get_execution_environment()
    return env

def configure_env(env: StreamExecutionEnvironment) -> None:
    # cfg = Configuration()
    # cfg.set_string("state.backend", "rocksdb")
    # cfg.set_string("state.checkpoint-storage", "filesystem")
    # cfg.set_string("state.checkpoints.dir", STATE_DIR)
    # env.configure(cfg)
    # env.enable_checkpointing(30_000)
    env.set_python_requirements(
        requirements_file_path="/app/processor/requirements.txt"
    )
    # env.set_parallelism(DESIRED_PARTITIONS)

def build_pipeline(env: StreamExecutionEnvironment) -> None:
    aggregator.build(env)

def submit(env: StreamExecutionEnvironment, job_name: str = "crypto-ticker-processor"):
    # you can switch --detached off to block here and see logs
    env.execute(job_name)

def main():
    env = create_env()
    configure_env(env)
    build_pipeline(env)
    submit(env)

if __name__ == "__main__":
    main()