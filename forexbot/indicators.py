import pandas as pd

def add_indicators(candles: pd.DataFrame) -> pd.DataFrame:
    df = candles.copy()
    df["ema_fast"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=26, adjust=False).mean()
    delta = df["close"].diff()
    gains, losses = delta.clip(lower=0), -delta.clip(upper=0)
    avg_gain = gains.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = losses.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, float("nan"))
    df["rsi"] = 100 - (100 / (1 + rs))
    prev = df["close"].shift(1)
    tr = pd.concat([df["high"]-df["low"], (df["high"]-prev).abs(), (df["low"]-prev).abs()], axis=1).max(axis=1)
    df["atr"] = tr.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    return df
