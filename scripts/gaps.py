"""List models missing core specs or a USD price. Read only.

    py scripts/gaps.py                     <- Thai for-sale models, all brands
    py scripts/gaps.py --status sold
    py scripts/gaps.py --status thai       <- anything with a Thai price
    py scripts/gaps.py --status all --brand pioneer

Watts are not expected on non-amps. ¥ list price and USD MSRP are not
treated as gaps (see NEEDS_DATA.md).
"""
import argparse
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DATA = Path(__file__).resolve().parent.parent / "data"
BRANDS = ["sansui", "marantz", "pioneer"]
CORE = {"year_start": "year", "watts_per_channel": "watts", "freq_response_hz": "freq",
        "thd_percent": "thd", "weight_kg": "wt", "avg_price_usd_3mo": "price"}
NONAMP = {"Tuner", "Preamp", "Tape Deck", "Reverb Unit", "Quad Synth", "Quad Decoder"}
STATUS = {
    "for-sale": lambda e: e.get("thb_status") == "For sale",
    "sold": lambda e: e.get("thb_status") == "Sold",
    "thai": lambda e: bool(e.get("price_thb_listings")),
    "all": lambda e: True,
}


def missing(e):
    out = []
    for f, short in CORE.items():
        if f == "watts_per_channel" and (e.get("type") or "") in NONAMP:
            continue
        if e.get(f) in (None, "", [], 0):
            out.append(short)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", default="for-sale", choices=STATUS)
    ap.add_argument("--brand", choices=BRANDS)
    a = ap.parse_args()

    total = 0
    for brand in [a.brand] if a.brand else BRANDS:
        db = json.load(open(DATA / f"{brand}.json", encoding="utf-8-sig"))
        rows = [(e, missing(e)) for e in db if STATUS[a.status](e)]
        rows = [(e, m) for e, m in rows if m]
        print(f"=== {brand.upper()} ({len(rows)}) ===")
        for e, m in sorted(rows, key=lambda r: r[0]["jdm_model"]):
            print(f"  {e['jdm_model']:20s} {e.get('type') or '-':16s} {', '.join(m)}")
        total += len(rows)
    print(f"\n{total} models with gaps ({a.status}).")


if __name__ == "__main__":
    main()
