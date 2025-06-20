import pytest
from types import SimpleNamespace
from processor.timestampers import TradeTimestampAssigner
from processor.models import Trade


def test_extract_timestamp():
    assigner = TradeTimestampAssigner()
    trade = Trade(symbol="X", price=1.0, size=1.0, event_ts=12345678)
    result = assigner.extract_timestamp(trade, record_timestamp=None)
    assert result == 12345678
