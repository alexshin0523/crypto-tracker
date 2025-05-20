from typing import Iterable
from pyflink.datastream.functions import ProcessWindowFunction
from pyflink.common import Row
from .models import Candle, Trade
from .schema import candle_to_row

class OHLCVWindowFunction(ProcessWindowFunction):

    def process(
            self,
            key: str,
            context: ProcessWindowFunction.Context,
            elements: Iterable[Trade],
    ) -> Iterable[Row]:
        if not elements:
            return None
        prices  = [t.price for t in elements]
        volumes = [t.size  for t in elements]

        yield candle_to_row(
            type("Candle", (), dict(         # tmp object; we only need attrs
                symbol=key,
                interval="1m",
                window_start=context.window().start,
                window_end=context.window().end,
                open=prices[0],
                high=max(prices),
                low=min(prices),
                close=prices[-1],
                volume=sum(volumes),
            ))()
        )
