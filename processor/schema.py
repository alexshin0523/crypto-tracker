from pyflink.common import Types, Row

CANDLE_TYPE = Types.ROW([
    Types.STRING(),   # symbol
    Types.STRING(),   # interval
    Types.LONG(),     # window_start (epoch-ms)
    Types.LONG(),     # window_end   (epoch-ms)
    Types.FLOAT(),    # open
    Types.FLOAT(),    # high
    Types.FLOAT(),    # low
    Types.FLOAT(),    # close
    Types.FLOAT(),    # volume
])

# optional helper for building a Row from a Candle dataclass
def candle_to_row(candle) -> Row:
    return Row(
        candle.symbol,
        candle.interval,
        candle.window_start,
        candle.window_end,
        candle.open,
        candle.high,
        candle.low,
        candle.close,
        candle.volume,
    )