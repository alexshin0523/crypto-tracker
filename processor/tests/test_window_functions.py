import pytest
from processor.window_functions import OHLCVWindowFunction
from processor.models import Trade

# Minimal stubs to mimic Flink's context.window()
class DummyWindow:
    def __init__(self, start, end):
        self.start = start
        self.end   = end

class DummyContext:
    def __init__(self, start, end):
        self._w = DummyWindow(start, end)
    def window(self):
        return self._w

def test_ohlcv_window_function_yields_correct_row():
    fn = OHLCVWindowFunction("1s")
    trades = [
        Trade(symbol="XYZ", price=1.0, size=2.0, event_ts=1000),
        Trade(symbol="XYZ", price=3.0, size=1.5, event_ts=2000),
        Trade(symbol="XYZ", price=2.0, size=0.5, event_ts=3000),
    ]

    # window [0, 60000)
    out = list(fn.process("XYZ", DummyContext(0, 60000), trades))
    assert len(out) == 1
    row = out[0]

    # Row layout: [symbol, interval, window_start, window_end,
    #              open, high, low, close, volume]
    assert row[0] == "XYZ"
    assert row[1] == "1m"
    assert row[2] == 0
    assert row[3] == 60000
    assert row[4] == 1.0           # open
    assert row[5] == 3.0           # high
    assert row[6] == 1.0           # low
    assert row[7] == 2.0           # close
    assert pytest.approx(row[8], rel=1e-6) == 2.0 + 1.5 + 0.5  # volume

def test_empty_window_yields_nothing():
    fn = OHLCVWindowFunction("1s")
    out = list(fn.process("NOP", DummyContext(0, 60000), []))
    assert out == []  # no trades → no candle