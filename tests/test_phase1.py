import pandas as pd
import pytest
from forexbot.data import validate_candles
from forexbot.strategy import latest_signal, Signal
from forexbot.paper import record_paper_entry, list_paper_trades

def candles(n=80):
    times = pd.date_range("2024-01-01", periods=n, freq="h", tz="UTC")
    close = [1.10 + i * 0.0005 for i in range(n)]
    return pd.DataFrame({"time": times, "open": close, "high": [x+0.001 for x in close],
        "low": [x-0.001 for x in close], "close": close, "volume": [100]*n})

def test_validates_and_sorts_candles():
    result = validate_candles(candles().sample(frac=1, random_state=2))
    assert result["time"].is_monotonic_increasing and len(result) == 80

def test_rejects_invalid_high():
    df = candles(); df.loc[0, "high"] = 0.5
    with pytest.raises(ValueError): validate_candles(df)

def test_signal_is_structured():
    signal = latest_signal(validate_candles(candles()), "EUR_USD")
    assert signal.action in {"BUY", "SELL", "HOLD"} and signal.symbol == "EUR_USD"

def test_paper_trade_duplicate_guard(tmp_path):
    path = str(tmp_path / "paper.db")
    sig = Signal("EUR_USD", "2024-01-01T00:00:00+00:00", "BUY", 1.1, 55.0, 0.001, "test")
    assert record_paper_entry(sig, 1000, path) == 1
    with pytest.raises(RuntimeError): record_paper_entry(sig, 1000, path)
    assert len(list_paper_trades(path)) == 1
