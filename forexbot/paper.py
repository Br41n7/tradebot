import sqlite3
from pathlib import Path
from .config import PAPER_DB_PATH
from .strategy import Signal

def _connect(db_path=PAPER_DB_PATH):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("""CREATE TABLE IF NOT EXISTS paper_trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT NOT NULL,
        side TEXT NOT NULL CHECK(side IN ('BUY','SELL')), units REAL NOT NULL CHECK(units > 0),
        entry_price REAL NOT NULL CHECK(entry_price > 0), signal_time TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'OPEN' CHECK(status IN ('OPEN','CLOSED')))""")
    conn.commit()
    return conn

def record_paper_entry(signal: Signal, units: float, db_path=PAPER_DB_PATH):
    """Record virtual entry only; intentionally contains no broker execution code."""
    if signal.action not in {"BUY", "SELL"}:
        return None
    if units <= 0:
        raise ValueError("units must be positive")
    with _connect(db_path) as conn:
        exists = conn.execute("SELECT id FROM paper_trades WHERE symbol=? AND status='OPEN' LIMIT 1",
                              (signal.symbol,)).fetchone()
        if exists:
            raise RuntimeError(f"An open paper position already exists for {signal.symbol}.")
        cur = conn.execute("INSERT INTO paper_trades(symbol,side,units,entry_price,signal_time) VALUES(?,?,?,?,?)",
                           (signal.symbol, signal.action, float(units), float(signal.close), signal.time))
        conn.commit()
        return int(cur.lastrowid)

def list_paper_trades(db_path=PAPER_DB_PATH):
    with _connect(db_path) as conn:
        return conn.execute("SELECT id,symbol,side,units,entry_price,signal_time,status FROM paper_trades ORDER BY id DESC").fetchall()
