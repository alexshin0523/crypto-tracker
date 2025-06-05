from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.state_backend import EmbeddedRocksDBStateBackend
from pyflink.common import Configuration
from processor import aggregator, config
from processor.config import STATE_DIR
import os

def create_env(connector_jar: str = None) -> StreamExecutionEnvironment:


    env = StreamExecutionEnvironment.get_execution_environment()
    if connector_jar:
        env.add_jars(f"file://{connector_jar}")
    return env

def configure_env(env: StreamExecutionEnvironment) -> None:
    cfg = Configuration()
    cfg.set_string("state.backend", "rocksdb")
    cfg.set_string("state.checkpoint-storage", "filesystem")
    cfg.set_string("state.checkpoints.dir", STATE_DIR)
    env.configure(cfg)
    env.enable_checkpointing(30_000)
    env.set_python_requirements(
        requirements_file_path="/app/processor/requirements.txt"
    )
    # this_dir = os.path.dirname(__file__)                # e.g. "/home/bob/crypto-tracker/jobs"
    # project_root = os.path.abspath(os.path.join(this_dir, os.pardir))
    # processor_folder = os.path.join(project_root, "processor")
    # env.add_python_file(processor_folder)

def build_pipeline(env: StreamExecutionEnvironment) -> None:
    aggregator.build(env)

def submit(env: StreamExecutionEnvironment, job_name: str = "crypto-ticker-processor"):
    # you can switch --detached off to block here and see logs
    env.execute(job_name)

def main():
    jar = os.getenv("CONNECTOR_JAR")
    env = create_env(jar)
    configure_env(env)
    build_pipeline(env)
    submit(env)

if __name__ == "__main__":
    main()