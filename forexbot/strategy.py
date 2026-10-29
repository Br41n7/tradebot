from dataclasses import dataclass
import pandas as pd
from .indicators import add_indicators

@dataclass(frozen=True)
class Signal:
    symbol: str
    time: str
    action: str
    close: float
    rsi: float | None
    atr: float | None
    reason: str

def latest_signal(candles: pd.DataFrame, symbol: str = "EUR_USD") -> Signal:
    if len(candles) < 30:
        raise ValueError("At least 30 completed candles are required.")
    row = add_indicators(candles).iloc[-1]
    action, reason = "HOLD", "No strategy condition met."
    if pd.notna(row["rsi"]) and row["ema_fast"] > row["ema_slow"] and 50 <= row["rsi"] <= 70:
        action, reason = "BUY", "Fast EMA above slow EMA and RSI confirms positive momentum."
    elif pd.notna(row["rsi"]) and row["ema_fast"] < row["ema_slow"] and 30 <= row["rsi"] <= 50:
        action, reason = "SELL", "Fast EMA below slow EMA and RSI confirms negative momentum."
    return Signal(symbol, row["time"].isoformat(), action, float(row["close"]),
                  None if pd.isna(row["rsi"]) else float(row["rsi"]),
                  None if pd.isna(row["atr"]) else float(row["atr"]), reason)
