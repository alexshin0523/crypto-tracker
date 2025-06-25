import json
from dataclasses import dataclass, field
from ..config import REDIS_NODES, REDIS_PASSWORD, REDIS_USE_TLS, REDIS_RETENTION
from pyflink.java_gateway import get_gateway

_jvm = get_gateway().jvm

FlinkJedisClusterConfig = _jvm.org.apache.flink.streaming.connectors.redis.common.config.FlinkJedisClusterConfig
RedisMapper = _jvm.org.apache.flink.streaming.connectors.redis.common.mapper.RedisMapper
RedisCommandDescription = _jvm.org.apache.flink.streaming.connectors.redis.common.mapper.RedisCommandDescription
RedisCommand = _jvm.org.apache.flink.streaming.connectors.redis.common.mapper.RedisCommand
RedisSink = _jvm.org.apache.flink.streaming.connectors.redis.RedisSink

@dataclass(frozen=True)
class RedisConfig:
    nodes: list[tuple[str,int]] = field(default_factory=lambda: REDIS_NODES.copy())
    password: str = REDIS_PASSWORD
    use_tls: bool = REDIS_USE_TLS
    retention: int = REDIS_RETENTION

class RedisSinkFactory:
    def __init__(self, cfg: RedisConfig):
        self.cfg = cfg

    def _build_jedis_conf(self):
        builder = FlinkJedisClusterConfig.builder()
        for host, port in self.cfg.nodes:
            builder.setNode(host, port)
        if self.cfg.password:
            builder.setPassword(self.cfg.password)
        if self.cfg.use_tls:
            builder.setUseSsl(True)
        return builder.setMaxTotal(50).build()

    class CandleMapper(RedisMapper):
        def __init__(self, retention: int):
            self.retention = retention

        def getCommandDescription(self):
            lua = """
            local ts_key = KEYS[1]..":timestamps"
            local data_key = KEYS[1]..":data"
            redis.call("ZADD", ts_key, ARGV[1], ARGV[1])
            redis.call("HSET", data_key, ARGV[1], ARGV[2])
            local removed = redis.call("ZREMRANGEBYRANK", ts_key, 0, -ARGV[3]-1)
            if removed > 0 then
              local old = redis.call("ZRANGE", ts_key, 0, removed-1)
              for _,ots in ipairs(old) do
                redis.call("HDEL", data_key, ots)
              end
            end
            return 1
            """
            return RedisCommandDescription(RedisCommand.EVAL, lua, numKeys=1)

        def getKeyFromData(self, t):
            data = json.loads(t.f1)
            return f"candles:{{{t.f0}}}-{data['interval']}"

        def getValueFromData(self, t):
            data = json.loads(t.f1)
            return [str(data["window_start"]), t.f1, str(self.retention)]

    def create_redis_sink(self):
        jedis_conf = self._build_jedis_conf()
        mapper     = self.CandleMapper(self.cfg.retention)
        sink       = RedisSink(jedis_conf, mapper)
        sink.setEnableXaTransactions(True)
        return sink
