import os
from dotenv import load_dotenv

load_dotenv()
OANDA_PRACTICE_TOKEN = os.getenv("OANDA_PRACTICE_TOKEN", "").strip()
OANDA_BASE_URL = os.getenv("OANDA_BASE_URL", "https://api-fxpractice.oanda.com").rstrip("/")
PAPER_DB_PATH = os.getenv("PAPER_DB_PATH", "data/paper.db")
if OANDA_BASE_URL != "https://api-fxpractice.oanda.com":
    raise RuntimeError("Safety guard: OANDA_BASE_URL must be https://api-fxpractice.oanda.com")
