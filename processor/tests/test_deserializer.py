import pytest
from processor.deserializer import json_to_trade
from processor.models import Trade

def test_json_to_trade_maps_binance_fields():
    # Binance “aggTrade” style payload has more fields than our Trade
    raw = (
        '{"e":"aggTrade","E":1690000000000,"s":"BTCUSDT",'
        '"p":"35000.0","q":"0.1","f":100,"l":200,"T":1690000000123,"m":false}'
    )
    trade = json_to_trade(raw)

    # It should ignore extra keys and pick exactly the ones our dataclass expects
    assert isinstance(trade, Trade)
    assert trade.symbol   == "BTCUSDT"
    assert trade.price    == 35000.0
    assert trade.size     == 0.1
    assert trade.event_ts == 1690000000000

    # If a required key is missing, it should raise KeyError
    with pytest.raises(KeyError):
        json_to_trade('{"s":"X","p":"1.0","q":"2.0"}')  # no "E"