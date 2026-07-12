"""Migrate avg_price_thb_3yr (single averaged number) -> price_thb_listings (list).

Wayne's rule: never average Thai prices; each price is a distinct listing and all
are shown. The four models averaged in the July 2026 update are split back into
their original listing prices. All other values become single-element lists.
"""
import json
from pathlib import Path

DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# July 2026 originals for the models that were wrongly averaged
SPLIT = {
    "AU-111":   [59000, 49000],
    "AU-5900":  [8900, 9500],
    "QRX-3500": [9900, 5800],
    "G-6700":   [18000, 18000],
}

migrated = 0
for e in db:
    val = e.pop("avg_price_thb_3yr", None)
    if e["jdm_model"] in SPLIT:
        e["price_thb_listings"] = SPLIT[e["jdm_model"]]
    elif val is not None:
        e["price_thb_listings"] = [val]
    else:
        e["price_thb_listings"] = []
    if e["price_thb_listings"]:
        migrated += 1

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print(f"Migrated. {migrated} models have THB listings.")
for jm, v in SPLIT.items():
    print(f"  {jm:10s} -> {v}")
