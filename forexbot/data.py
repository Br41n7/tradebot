from pathlib import Path
import pandas as pd
import requests
from .config import OANDA_PRACTICE_TOKEN, OANDA_BASE_URL

REQUIRED = ["time", "open", "high", "low", "close", "volume"]

def validate_candles(frame: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in REQUIRED if c not in frame.columns]
    if missing:
        raise ValueError(f"Missing candle columns: {missing}")
    out = frame[REQUIRED].copy()
    out["time"] = pd.to_datetime(out["time"], utc=True, errors="coerce")
    for col in ["open", "high", "low", "close", "volume"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out = out.dropna().sort_values("time").drop_duplicates("time").reset_index(drop=True)
    if out.empty:
        raise ValueError("No valid candle rows found")
    if (out[["open", "high", "low", "close"]] <= 0).any().any():
        raise ValueError("OHLC prices must be positive")
    if (out["high"] < out[["open", "close", "low"]].max(axis=1)).any():
        raise ValueError("Invalid candle: high is below another OHLC value")
    if (out["low"] > out[["open", "close", "high"]].min(axis=1)).any():
        raise ValueError("Invalid candle: low is above another OHLC value")
    return out

def load_csv(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Candle CSV not found: {p}")
    return validate_candles(pd.read_csv(p))

def fetch_oanda_candles(instrument="EUR_USD", granularity="H1", count=300) -> pd.DataFrame:
    """Read candles from OANDA practice API only; cannot place orders."""
    if not OANDA_PRACTICE_TOKEN:
        raise RuntimeError("Set OANDA_PRACTICE_TOKEN in .env to use OANDA practice candle data.")
    if not instrument.replace("_", "").isalnum():
        raise ValueError("Invalid instrument format")
    if not (10 <= int(count) <= 5000):
        raise ValueError("count must be between 10 and 5000")
    url = f"{OANDA_BASE_URL}/v3/instruments/{instrument}/candles"
    response = requests.get(url, params={"granularity": granularity, "count": int(count), "price": "M"},
        headers={"Authorization": f"Bearer {OANDA_PRACTICE_TOKEN}"}, timeout=20)
    response.raise_for_status()
    rows = []
    for candle in response.json().get("candles", []):
        if candle.get("complete", False):
            mid = candle.get("mid", {})
            rows.append({"time": candle["time"], "open": mid.get("o"), "high": mid.get("h"),
                         "low": mid.get("l"), "close": mid.get("c"), "volume": candle.get("volume", 0)})
    if not rows:
        raise RuntimeError("Provider returned no completed candles.")
    return validate_candles(pd.DataFrame(rows))
