from pyflink.common.watermark_strategy import TimestampAssigner

class TradeTimestampAssigner(TimestampAssigner):
    def extract_timestamp(self, trade, record_timestamp):
        return trade.event_ts