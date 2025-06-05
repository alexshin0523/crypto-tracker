import os
import pytest
from pyflink.common import Configuration
from processor.main import create_env, configure_env, build_pipeline

@pytest.fixture
def env():
    # point at the local shaded JAR
    yield create_env(os.environ.get("CONNECTOR_JAR"))

def test_env_creation(env):
    assert hasattr(env, "execute"), "Did not get a StreamExecutionEnvironment"

def test_env_configuration(env):
    configure_env(env)
    cfg = env.get_checkpoint_config()
    # checkpoint interval should be set to 30000 ms
    assert cfg.get_checkpoint_interval() == 30000

def test_pipeline_plan(env):
    configure_env(env)
    build_pipeline(env)
    plan_json = env.get_execution_plan()
    assert "FlinkKafkaConsumer" in plan_json
    assert "FlinkKafkaProducer" in plan_json