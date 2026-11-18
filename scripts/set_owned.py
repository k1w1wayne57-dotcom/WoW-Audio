"""Mark Wayne's own units `owned: true` and seed the private data/collection.json
with the purchase figures already recorded in the DB notes and his G-5700 cost sheet.
Dry run by default; --apply writes. collection.json is gitignored (local only)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from serve import load_db, save_db, DATA  # noqa: E402

OWNED = {
    "sansui": ["sansui-b-2102-1986", "sansui-au-alpha607-1st-gen-1976", "sansui-g-5700-1978",
               "sansui-au-d607-1979", "sansui-au-alpha507-1986"],
    "yamaha": ["yamaha-cr-2020-1977"],
}

# Only figures with a source. Everything else stays null.
SEED = {
    "sansui-b-2102-1986": {"status": "In use", "bought": "2026-08", "buy_thb": 20000,
        "notes": "Buy price from DB collector notes (Aug 2026, ฿20,000)."},
    "sansui-au-alpha607-1st-gen-1976": {"status": "In use"},
    "sansui-g-5700-1978": {"status": "In use", "buy_thb": 7500, "freight_thb": 2800, "parts_thb": 7778.6,
        "notes": "SN 819120062. From 'SansuiG5700 Costs.xlsx' Sheet1: buy ฿7,500, taxi ฿2,800, parts ฿7,778.60 (main filter caps outstanding then)."},
    "sansui-au-d607-1979": {"status": "In use", "bought": "2026-10", "buy_thb": 4900,
        "notes": "Buy price from DB collector notes (Oct 2026, ฿4,900)."},
    "sansui-au-alpha507-1986": {"status": "Donor", "buy_thb": 3700,
        "notes": "฿3,700 incl. delivery. TA7317P donor for the B-2102; to sell. SN 627067229."},
    "yamaha-cr-2020-1977": {"status": "Restoring", "bought": "2026-10", "buy_thb": 8000,
        "notes": "Buy price from DB collector notes (Oct 2026, ฿8,000). Arrived 18 Nov 2026; recap list in CR-2020 Cap Order.xlsx."},
}

apply = "--apply" in sys.argv
for brand, ids in OWNED.items():
    data, meta = load_db(brand)
    found = {r["id"]: r for r in data}
    for i in ids:
        r = found.get(i)
        if not r:
            sys.exit(f"missing id {i}")
        print(f"{brand}: {i} ({r['jdm_model']}) owned {r.get('owned')} -> True")
        r["owned"] = True
    if apply:
        save_db(data, meta)

path = DATA / "collection.json"
if path.exists():
    print("collection.json exists - not overwritten")
elif apply:
    path.write_text(json.dumps({"_note": "Private. Gitignored. Money in THB.", "items": SEED},
                               ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote", path)
print("APPLIED" if apply else "dry run - add --apply")
