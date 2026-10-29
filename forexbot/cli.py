import argparse, json
from dataclasses import asdict
from .data import load_csv, fetch_oanda_candles
from .strategy import latest_signal
from .paper import record_paper_entry, list_paper_trades

def main():
    parser = argparse.ArgumentParser(description="Forex analysis and paper trading only.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("signal", "paper"):
        p = sub.add_parser(name)
        p.add_argument("--provider", choices=["csv", "oanda"], default="csv")
        p.add_argument("--csv", help="CSV with time,open,high,low,close,volume")
        p.add_argument("--symbol", default="EUR_USD")
        p.add_argument("--granularity", default="H1")
        p.add_argument("--count", type=int, default=300)
        if name == "paper":
            p.add_argument("--units", type=float, default=1000)
    sub.add_parser("trades", help="List stored paper trades")
    args = parser.parse_args()
    if args.command == "trades":
        print(json.dumps(list_paper_trades(), indent=2)); return
    if args.provider == "oanda":
        candles = fetch_oanda_candles(args.symbol, args.granularity, args.count)
    else:
        if not args.csv:
            raise SystemExit("CSV mode requires --csv PATH.")
        candles = load_csv(args.csv)
    signal = latest_signal(candles, args.symbol)
    print(json.dumps(asdict(signal), indent=2))
    if args.command == "paper":
        trade_id = record_paper_entry(signal, args.units)
        print(f"Paper entry recorded: {trade_id}" if trade_id else "No paper entry: signal is HOLD.")

if __name__ == "__main__":
    main()
