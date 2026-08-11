#!/usr/bin/env python3
"""
Fetch the latest close for each Nifty index and write data.json.

Design choices:
- If a symbol fails or returns nothing, the previous value in data.json is kept,
  so a transient data-source hiccup never blanks a gauge.
- The dashboard reads this file at load; only `cur` and `date` per index are used
  (plus a top-level `updated` timestamp shown under the gauges).

Data source note:
- Uses Yahoo Finance via yfinance — zero-auth and fine for a personal board, but an
  unofficial endpoint that can change or rate-limit. VERIFY each ticker resolves.
  Confident: ^NSEI (Nifty 50), NIFTYSMLCAP250.NS (Smallcap 250),
  NIFTY_MICROCAP250.NS (Microcap 250).
  Double-check: NIFTY_MIDCAP_100.NS (Midcap 100), ^CRSLDX (Nifty 500) — Yahoo's
  Indian index symbols are inconsistent. If one returns empty, try the alternates
  listed beside it below.
- For anything you rely on, switch to a broker API you already have (Zerodha Kite,
  Upstox, Angel One) and store the key as a GitHub Actions secret.
"""

import json
import os
import datetime
import yfinance as yf

# name -> primary ticker (alternates in comments if the primary comes back empty)
TICKERS = {
    "Nifty 50":            "^NSEI",                 # alt: NIFTY_50.NS
    "Nifty Midcap 100":    "NIFTY_MIDCAP_100.NS",   # alt: ^CRSMID
    "Nifty Smallcap 250":  "NIFTYSMLCAP250.NS",     # alt: NIFTY_SMLCAP_250.NS
    "Nifty Microcap 250":  "NIFTY_MICROCAP250.NS",  # alt: NIFTY_MICROCAP_250.NS
    "Nifty 500":           "^CRSLDX",               # alt: NIFTY_500.NS
}

DATA_FILE = "data.json"
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


def load_existing():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def main():
    out = load_existing()
    for name, sym in TICKERS.items():
        try:
            series = yf.Ticker(sym).history(period="5d")["Close"].dropna()
            if len(series):
                out[name] = {
                    "cur": round(float(series.iloc[-1]), 2),
                    "date": series.index[-1].strftime("%-d %b %Y"),
                }
                print(f"OK    {name:20s} {sym:22s} -> {out[name]['cur']}")
            else:
                print(f"WARN  {name} ({sym}) returned no rows; keeping previous value")
        except Exception as e:
            print(f"WARN  {name} ({sym}) failed: {e}; keeping previous value")

    out["updated"] = datetime.datetime.now(IST).strftime("%-d %b %Y %H:%M IST")
    with open(DATA_FILE, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"wrote {DATA_FILE} (updated {out['updated']})")


if __name__ == "__main__":
    main()
