from pyflink.common import Types, Row

from processor.models import Candle

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

def row_to_candle(row):
    # If your CANDLE_TYPE fields come out in exactly this order:
    #   (symbol, open, high, low, close, volume)
    c = Candle(
        symbol=row[0],
        interval=row[1],
        window_start=row[2],
        window_end=row[3],
        open=row[4],
        high=row[5],
        low=row[6],
        close=row[7],
        volume=row[8],
    )
    return c.to_json()