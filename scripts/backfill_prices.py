"""
WoW Audio — one-time price backfill from HiFi Shark (uses scrape.py's engine).

Fills ONLY blank `avg_price_usd_3mo` on existing records, using the same
Playwright scraper + junk-filter + outlier trim as scrape.py. Never overwrites
a price you already have. Each fill is stamped with `auto_price` provenance and
a confidence tag; anything with too few real listings is left blank.

Slow (a real browser per model). Resumable: re-running skips records already
priced, and it saves after every write, so a crash loses nothing.

    python scripts/backfill_prices.py                 # all brands, blanks only
    python scripts/backfill_prices.py --brand marantz
    python scripts/backfill_prices.py --limit 5       # test on first 5 gaps
    python scripts/backfill_prices.py --months 6      # price window (default 6)

Writes a review file: scripts/backfill_prices_review.tsv
"""

import sys
import json
import time
import argparse
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scrape  # fetch_rendered, parse_hifishark, summarize_usd, hifishark_search_url
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
BRANDS = ["sansui", "marantz", "pioneer"]
TODAY = f"{datetime.date.today():%Y-%m}"
EMPTY = (None, "", "—", [], {})
MIN_LISTINGS = 5          # fewer than this = don't trust it, leave blank
MAX_SPREAD = 5            # high/low beyond this = incoherent sample (mixed
                          # variants, part-outs, multi-unit lots) -> leave blank
REVIEW = Path(__file__).resolve().parent / "backfill_prices_review.tsv"


def load_db(brand):
    path = DATA / f"{brand}.json"
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8-sig")), {
        "path": path, "bom": raw.startswith(b"\xef\xbb\xbf"), "crlf": b"\r\n" in raw}


def save_db(data, meta):
    s = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if meta["crlf"]:
        s = s.replace("\n", "\r\n")
    enc = s.encode("utf-8")
    if meta["bom"]:
        enc = b"\xef\xbb\xbf" + enc
    meta["path"].write_bytes(enc)


def price_one(brand, model, months):
    url = scrape.hifishark_search_url(brand, model)
    try:
        html = scrape.fetch_rendered(url, wait_selector="a.search-product-row")
    except Exception:
        return None
    listings = scrape.parse_hifishark(BeautifulSoup(html, "html.parser"), url)
    return scrape.summarize_usd(listings, months, model=model)


def in_years(rec, years):
    """years = (lo, hi) on year_start, or None for all."""
    if not years:
        return True
    y = rec.get("year_start")
    return isinstance(y, int) and years[0] <= y <= years[1]


def run(brands, months, limit, refresh=False, years=None):
    review = ["\t".join(["brand", "model", "median_usd", "n", "confidence",
                         "range", "status"])]
    done = attempted = 0
    for brand in brands:
        data, meta = load_db(brand)
        gaps = [r for r in data
                if (refresh or r.get("avg_price_usd_3mo") in EMPTY)
                and in_years(r, years)
                and (r.get("jdm_model") or r.get("model"))]
        if limit:
            gaps = gaps[:limit]
        what = "records to (re)price" if refresh else "records missing a price"
        print(f"{brand}: {len(gaps)} {what}", flush=True)
        for i, rec in enumerate(gaps, 1):
            model = str(rec.get("jdm_model") or rec.get("model")).strip()
            attempted += 1
            print(f"  [{brand} {i}/{len(gaps)}] {model} ...", end=" ", flush=True)
            s = price_one(brand, model, months)
            if not s or s["count"] < MIN_LISTINGS:
                n = s["count"] if s else 0
                print(f"skip (only {n} listings)", flush=True)
                review.append("\t".join([brand, model, "", str(n), "", "", "too few"]))
                time.sleep(0.5)
                continue
            # Quartile ratio, not high/low: one part-out listing shouldn't veto
            # an otherwise coherent sample the median already ignores.
            spread = s.get("q3", s["high"]) / max(s.get("q1", s["low"]), 1)
            if spread > MAX_SPREAD:
                print(f"skip (spread {spread:.0f}x — ${s['low']:,}-${s['high']:,}, "
                      f"incoherent)", flush=True)
                review.append("\t".join([brand, model, "", str(s["count"]), "",
                                         f"${s['low']:,}-${s['high']:,}", "spread"]))
                time.sleep(0.5)
                continue
            conf = "Medium" if s["count"] >= 8 else "Low"
            prev = rec.get("avg_price_usd_3mo")
            rec["avg_price_usd_3mo"] = s["median"]
            rec["price_basis"] = f"hifishark {months}mo listing median, asking prices (FX->USD) {TODAY}"
            rec["price_confidence"] = conf
            rec["last_price_check"] = TODAY
            rec["auto_price"] = {"source": "hifishark.com", "date": TODAY,
                                 "n": s["count"], "median_usd": s["median"]}
            if prev not in EMPTY and prev != s["median"]:
                rec["auto_price"]["previous_usd"] = prev   # keep the old figure visible
            save_db(data, meta)   # save after every write -> resumable
            done += 1
            print(f"${s['median']:,} (n={s['count']}, {conf})", flush=True)
            review.append("\t".join([brand, model, str(s["median"]), str(s["count"]),
                                     conf, f"${s['low']:,}-${s['high']:,}", "written"]))
            time.sleep(0.5)
    REVIEW.write_text("\n".join(review), encoding="utf-8")
    print(f"\n=== DONE: {done} prices written, {attempted - done} skipped "
          f"(of {attempted} attempted) ===", flush=True)
    print(f"review: {REVIEW}", flush=True)


def main():
    ap = argparse.ArgumentParser(description="Backfill prices from HiFi Shark.")
    ap.add_argument("--brand", choices=BRANDS)
    ap.add_argument("--months", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--refresh", action="store_true",
                    help="also re-price records that already have a price")
    ap.add_argument("--years", metavar="LO-HI",
                    help="only records with year_start in this range, e.g. 1970-1979")
    args = ap.parse_args()
    years = None
    if args.years:
        lo, hi = args.years.split("-")
        years = (int(lo), int(hi))
    run([args.brand] if args.brand else BRANDS, args.months, args.limit,
        refresh=args.refresh, years=years)


if __name__ == "__main__":
    main()
