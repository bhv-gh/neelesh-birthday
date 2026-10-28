"""Fetch public market data. Never substitute fictional stock prices."""
import concurrent.futures
import datetime as dt
import json
import math
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json,text/html"}


def get(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=12) as response:
        return response.read().decode("utf-8")


def valid_price(value):
    return isinstance(value, (int, float)) and math.isfinite(value) and value > 0


def fetch(symbol):
    for host in ("query1.finance.yahoo.com", "query2.finance.yahoo.com"):
        try:
            result = json.loads(get(
                f"https://{host}/v8/finance/chart/{symbol}?range=1mo&interval=1d"
            ))["chart"]["result"][0]
            meta = result["meta"]
            price = meta["regularMarketPrice"]
            if not valid_price(price):
                raise ValueError("Invalid market price")
            previous = meta.get("chartPreviousClose")
            closes = result["indicators"]["quote"][0]["close"]
            history = [round(p, 2) for p in closes if valid_price(p)]
            # Compare against the prior daily close, not the start of the month.
            stamps = result.get("timestamp", [])
            market_day = dt.datetime.fromtimestamp(meta["regularMarketTime"], dt.timezone.utc).date()
            prior = [p for t, p in zip(stamps, closes)
                     if valid_price(p) and dt.datetime.fromtimestamp(t, dt.timezone.utc).date() < market_day]
            previous = prior[-1] if prior else previous
            return symbol, {
                "price": round(price, 2), "currency": meta.get("currency", "USD"),
                "change": round(price - previous, 2) if valid_price(previous) else None,
                "changePercent": round((price / previous - 1) * 100, 2) if valid_price(previous) else None,
                "asOf": dt.datetime.fromtimestamp(meta["regularMarketTime"], dt.timezone.utc).isoformat(),
                "source": "Yahoo Finance", "sourceUrl": f"https://finance.yahoo.com/quote/{symbol}/",
                "history": history, "historyLabel": "Past month · daily closes", "timeType": "market",
            }
        except Exception as error:
            print(f"{symbol}: {host} unavailable ({type(error).__name__})")
    try:
        page = get(f"https://www.google.com/finance/quote/{symbol}:NASDAQ?hl=en")
        match = re.search(r'data-last-price="([\d.]+)"', page)
        if not match:
            match = re.search(r'class="YMlKec fxKbKc">\$([\d,.]+)<', page)
        if not match:
            raise ValueError("Price not found")
        price = float(match.group(1).replace(",", ""))
        if not valid_price(price):
            raise ValueError("Invalid price")
        return symbol, {
            "price": price, "currency": "USD", "change": None, "changePercent": None,
            "asOf": dt.datetime.now(dt.timezone.utc).isoformat(),
            "source": "Google Finance", "sourceUrl": f"https://www.google.com/finance/quote/{symbol}:NASDAQ",
            "history": [], "timeType": "retrieved",
        }
    except Exception as error:
        print(f"{symbol}: quote refresh failed ({type(error).__name__}); retaining previous snapshot")
        return symbol, None


def main():
    path = ROOT / "quotes.json"
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        data = {"updatedAt": None, "quotes": {}}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        for symbol, quote in executor.map(fetch, ("GOOGL", "META")):
            if quote:
                data["quotes"][symbol] = quote
                print(f"{symbol}: ${quote['price']:.2f} via {quote['source']}")
    data["updatedAt"] = dt.datetime.now(dt.timezone.utc).isoformat()
    path.write_text(json.dumps(data, indent=2) + "\n")


if __name__ == "__main__":
    main()
