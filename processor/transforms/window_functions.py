from pyflink.datastream.functions import ProcessWindowFunction
from pyflink.datastream.functions import AggregateFunction
from pyflink.common import Row
from typing import Iterable

from processor.models import Trade, CandleAccumulator, Candle
from processor.schema import candle_to_row, row_to_candle

class OHLCVAggregateFunction(AggregateFunction):

    def create_accumulator(self) -> CandleAccumulator:
        return CandleAccumulator()

    def add(self, trade: Trade, acc: CandleAccumulator) -> CandleAccumulator:
        price, size = trade.price, trade.size
        if acc.open is None:
            acc.open = price
        acc.high   = max(acc.high, price)
        acc.low    = min(acc.low, price)
        acc.close  = price
        acc.volume += size
        return acc

    def get_result(self, acc: CandleAccumulator) -> CandleAccumulator:
        return acc

    def merge(self, a: CandleAccumulator, b: CandleAccumulator) -> CandleAccumulator:
        merged = CandleAccumulator(
            open=   a.open   if a.open   is not None else b.open,
            high=   max(a.high,   b.high),
            low=    min(a.low,    b.low),
            close=  b.close  if b.close  is not None else a.close,
            volume= a.volume + b.volume
        )
        return merged


class OHLCVWindowFunction(ProcessWindowFunction):

    def __init__(self, interval: str):
        super().__init__()
        self.interval = interval

    def process(
            self,
            key: str,
            context: ProcessWindowFunction.Context,
            accs: Iterable[CandleAccumulator],
    ) -> Iterable[Row]:
        acc = next(iter(accs))

        # build your final Candle object
        candle = Candle(
            symbol=key,
            interval=self.interval,
            window_start=context.window().start,
            window_end=context.window().end,
            open=acc.open,
            high=acc.high,
            low=acc.low,
            close=acc.close,
            volume=acc.volume,
        )
        # emit via the Collector
        yield candle_to_row(candle)
