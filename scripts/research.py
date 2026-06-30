"""
WoW Audio price research helper.

Looks up Sansui model listings on HiFi Shark and reports average price, listing count,
date range, lowest and highest. Optionally writes results back into data/sansui.json.

Usage:
    python scripts/research.py "AU-111"
    python scripts/research.py all
    python scripts/research.py "AU-111" --update

Requires: requests, beautifulsoup4 (pip install requests beautifulsoup4)
"""

import sys
import json
import re
import argparse
import datetime
import time
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run: pip install requests beautifulsoup4")
    sys.exit(1)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "sansui.json"
HIFISHARK_SEARCH_URL = "https://hifishark.com/search"
HEADERS = {"User-Agent": "Mozilla/5.0 (WoW Audio research script; personal use)"}


def load_db():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(data):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def search_hifishark(model_name):
    """Search HiFi Shark for a model and return a list of {title, price} dicts."""
    query = f"sansui {model_name}"
    try:
        resp = requests.get(HIFISHARK_SEARCH_URL, params={"s": query}, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  Request failed for '{model_name}': {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    # NOTE: selectors are best-effort and may need adjusting if HiFi Shark changes its markup.
    for item in soup.select(".listing-item, .product-item, article"):
        title_el = item.select_one(".title, h2, h3")
        price_el = item.select_one(".price")
        if not title_el or not price_el:
            continue
        price_match = re.search(r"[\d,]+(\.\d+)?", price_el.get_text())
        if not price_match:
            continue
        price = float(price_match.group(0).replace(",", ""))
        results.append({"title": title_el.get_text(strip=True), "price": price})
    return results


def summarize(results):
    if not results:
        return None
    prices = [r["price"] for r in results]
    return {
        "count": len(prices),
        "avg": round(sum(prices) / len(prices), 2),
        "low": min(prices),
        "high": max(prices),
    }


def research_model(model_name, update=False, db=None):
    print(f"Researching: {model_name}")
    results = search_hifishark(model_name)
    summary = summarize(results)

    if not summary:
        print("  No listings found.")
        return

    print(f"  Listings: {summary['count']}  Avg: ${summary['avg']}  "
          f"Low: ${summary['low']}  High: ${summary['high']}")

    if update and db is not None:
        today = datetime.date.today().strftime("%Y-%m")
        matched = False
        for entry in db:
            if entry.get("jdm_model", "").lower() == model_name.lower():
                entry["avg_price_usd_1yr"] = summary["avg"]
                entry["price_confidence"] = "Medium" if summary["count"] >= 3 else "Low"
                entry["last_price_check"] = today
                matched = True
        if not matched:
            print(f"  Warning: no matching jdm_model '{model_name}' found in sansui.json — not updated.")


def main():
    parser = argparse.ArgumentParser(description="WoW Audio price research helper")
    parser.add_argument("model", help='Model name (e.g. "AU-111") or "all" to research every model')
    parser.add_argument("--update", action="store_true", help="Write results back into sansui.json")
    args = parser.parse_args()

    db = load_db() if args.update else None

    if args.model.lower() == "all":
        all_models = load_db()
        for entry in all_models:
            research_model(entry["jdm_model"], update=args.update, db=db)
            time.sleep(2)  # be polite to the server
    else:
        research_model(args.model, update=args.update, db=db)

    if args.update and db is not None:
        save_db(db)
        print(f"\nUpdated {DB_PATH}")


if __name__ == "__main__":
    main()
